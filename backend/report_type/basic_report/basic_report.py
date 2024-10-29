from fastapi import WebSocket
from typing import Any, List, Dict, Optional
from gpt_researcher import GPTResearcher
from serper import SerperSearch

class BasicReport:
    # Predefined sources to search
    FIXED_SOURCES = [
        "dnb.com",
        "trustedshops.de",
        "billiger.de",
        "webvalid.de",
        "google.de"
    ]

    def __init__(
        self,
        query: str,
        report_type: str,
        report_source: str,
        source_urls: Optional[List[str]],
        tone: Any,
        config_path: str,
        websocket: WebSocket,
        headers=None
    ):
        self.query = query
        self.report_type = report_type
        self.report_source = report_source
        self.initial_urls = source_urls or []
        self.tone = tone
        self.config_path = config_path
        self.websocket = websocket
        self.headers = headers or {}

    async def _search_sources(self) -> Dict:
        """
        Search across all specified sources including fixed sources and initial URL
        """
        all_results = {}

        # First search the initial URLs if provided
        for url in self.initial_urls:
            try:
                searcher = SerperSearch(url)
                results = searcher.search_all()
                all_results[url] = results
                await self.websocket.send_text(f"Completed search for {url}")
            except Exception as e:
                await self.websocket.send_text(f"Error searching {url}: {str(e)}")

        # Then search the fixed sources
        for source in self.FIXED_SOURCES:
            try:
                searcher = SerperSearch(source)
                # For fixed sources, we'll include the original query in the search
                modified_query = f"{self.query} site:{source}"
                searcher.url = modified_query  # Override the URL with the modified query
                results = searcher.search_all()
                all_results[source] = results
                await self.websocket.send_text(f"Completed search for {source}")
            except Exception as e:
                await self.websocket.send_text(f"Error searching {source}: {str(e)}")

        return all_results

    def _process_search_results(self, search_results: Dict) -> List[str]:
        """
        Process search results into a list of relevant URLs
        """
        processed_urls = set()

        for source, results in search_results.items():
            # Process organic results
            for result in results.get('organic_results', []):
                if 'href' in result:
                    processed_urls.add(result['href'])

            # Process news results
            for news in results.get('news_results', []):
                if 'link' in news:
                    processed_urls.add(news['link'])

        return list(processed_urls)

    async def run(self):
        """
        Run the research process including multi-source search
        """
        # Notify start of search
        await self.websocket.send_text("Starting multi-source search...")

        # Perform searches across all sources
        search_results = await self._search_sources()

        # Process results into a list of URLs
        processed_urls = self._process_search_results(search_results)

        # Update source_urls with all found URLs
        self.source_urls = processed_urls

        # Notify completion of search phase
        await self.websocket.send_text(f"Found {len(processed_urls)} relevant URLs")

        # Initialize researcher with gathered URLs
        researcher = GPTResearcher(
            query=self.query,
            report_type=self.report_type,
            report_source=self.report_source,
            source_urls=self.source_urls,
            tone=self.tone,
            config_path=self.config_path,
            websocket=self.websocket,
            headers=self.headers
        )

        # Conduct research and generate report
        await researcher.conduct_research()
        report = await researcher.write_report()

        # Include sources in report
        source_summary = "\n\nSources searched:\n" + \
                        "\n".join([f"- {source}" for source in self.FIXED_SOURCES]) + \
                        "\nInitial URLs:\n" + \
                        "\n".join([f"- {url}" for url in self.initial_urls])

        return report + source_summary