from gpt_researcher import GPTResearcher
import asyncio


async def get_report(query: str, report_source: str, sources: list) -> str:
    researcher = GPTResearcher(query=query, report_source=report_source, source_urls=sources)
    research_context = await researcher.conduct_research()
    return await researcher.write_report()

if __name__ == "__main__":
    query = "Preismaschine"
    report_source = "static"
    sources = [
        "https://www.google.de",
        "https://www.billiger.de",
        "https://www.google.de",
        "https://www.bloomberg.de",
        "https://www.handelsregister.de",
        "https://www.wappalyzer.com/lookup/",
        "https://opencorporates.com/companies/de",
        "https://www.trustedshops.de"
    ]

    report = asyncio.run(get_report(query=query, report_source=report_source, sources=sources))
    print(report)
