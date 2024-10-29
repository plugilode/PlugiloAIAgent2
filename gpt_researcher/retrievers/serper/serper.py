#!/usr/bin/env python3
"""
Serper API Integration Module

This module provides a comprehensive interface to the Serper API,
allowing searches across multiple Google services (web, images, news)
and URL scraping capabilities.

Required Environment Variables:
    SERPER_API_KEY: Your Serper API key from https://serper.dev/

Usage:
    from serper import SerperSearch
    searcher = SerperSearch("example.com")
    results = searcher.search_all()
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime

class SerperAPIError(Exception):
    """Custom exception for Serper API related errors"""
    pass

class SerperSearch:
    """
    Enhanced Google Serper Retriever with multiple search types

    This class provides methods to search across different Google services
    and scrape URLs using the Serper API.
    """

    # API endpoints
    SEARCH_ENDPOINT = "https://google.serper.dev/search"
    IMAGES_ENDPOINT = "https://google.serper.dev/images"
    NEWS_ENDPOINT = "https://google.serper.dev/news"
    SCRAPE_ENDPOINT = "https://scrape.serper.dev"

    def __init__(self, url: str):
        """
        Initialize the SerperSearch object

        Args:
            url (str): Company URL to search for

        Raises:
            SerperAPIError: If the API key is not found in environment variables
        """
        self.url = url
        self.api_key = self._get_api_key()
        self.base_headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        self.base_params = {
            "location": "Germany",
            "gl": "de",
            "hl": "de",
            "num": 30,
            "autocorrect": False
        }

    def _get_api_key(self) -> str:
        """
        Get the Serper API key from environment variables

        Returns:
            str: The API key

        Raises:
            SerperAPIError: If the API key is not found
        """
        try:
            api_key = os.environ["SERPER_API_KEY"]
            if not api_key:
                raise SerperAPIError("SERPER_API_KEY environment variable is empty")
            return api_key
        except KeyError:
            raise SerperAPIError(
                "Serper API key not found. Please set the SERPER_API_KEY environment variable. "
                "You can get a key at https://serper.dev/"
            )

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make a request to the Serper API

        Args:
            endpoint (str): API endpoint to call
            params (dict): Parameters to send with the request

        Returns:
            Optional[Dict]: JSON response from the API or None if request failed
        """
        try:
            data = json.dumps(params)
            resp = requests.post(
                endpoint,
                headers=self.base_headers,
                data=data,
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            return None

    def search_url(self, max_results: int = 30) -> List[Dict]:
        """
        Search for the URL in Google Search

        Args:
            max_results (int): Maximum number of results to return

        Returns:
            List[Dict]: List of search results
        """
        print(f"Searching URL {self.url} in Google Search...")

        params = self.base_params.copy()
        params["q"] = self.url
        params["num"] = max_results

        results = self._make_request(self.SEARCH_ENDPOINT, params)
        if not results:
            return []

        return self._process_organic_results(results)

    def search_images(self, max_results: int = 30) -> List[Dict]:
        """
        Search for images related to the URL

        Args:
            max_results (int): Maximum number of results to return

        Returns:
            List[Dict]: List of image search results
        """
        print(f"Searching images for {self.url}...")

        params = self.base_params.copy()
        params["q"] = self.url
        params["num"] = max_results

        results = self._make_request(self.IMAGES_ENDPOINT, params)
        return results.get("images", []) if results else []

    def search_news(self, max_results: int = 30) -> List[Dict]:
        """
        Search for news related to the URL

        Args:
            max_results (int): Maximum number of results to return

        Returns:
            List[Dict]: List of news search results
        """
        print(f"Searching news for {self.url}...")

        params = self.base_params.copy()
        params["q"] = self.url
        params["num"] = max_results

        results = self._make_request(self.NEWS_ENDPOINT, params)
        return results.get("news", []) if results else []

    def scrape_url(self) -> Dict:
        """
        Scrape the content of the URL

        Returns:
            Dict: Scraped content from the URL
        """
        print(f"Scraping content from {self.url}...")

        params = {"url": self.url}
        return self._make_request(self.SCRAPE_ENDPOINT, params) or {}

    def _process_organic_results(self, results: Dict) -> List[Dict]:
        """
        Process organic search results

        Args:
            results (Dict): Raw results from the API

        Returns:
            List[Dict]: Processed search results
        """
        processed_results = []

        for result in results.get("organic", []):
            if "youtube.com" in result["link"]:
                continue

            processed_results.append({
                "title": result["title"],
                "href": result["link"],
                "body": result["snippet"]
            })

        return processed_results

    def search_all(self) -> Dict[str, Union[List[Dict], Dict]]:
        """
        Perform all types of searches and return combined results

        Returns:
            Dict[str, Union[List[Dict], Dict]]: Combined results from all search types
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "url": self.url,
            "organic_results": self.search_url(),
            "image_results": self.search_images(),
            "news_results": self.search_news(),
            "url_content": self.scrape_url()
        }


def main():
    """
    Example usage of the SerperSearch class
    """
    # Example URL
    target_url = "example.com"

    try:
        # Initialize searcher
        searcher = SerperSearch(target_url)

        # Get all results
        results = searcher.search_all()

        # Print summary
        print("\nSearch Results Summary:")
        print(f"URL: {results['url']}")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Organic Results: {len(results['organic_results'])}")
        print(f"Image Results: {len(results['image_results'])}")
        print(f"News Results: {len(results['news_results'])}")
        print(f"URL Content Size: {len(str(results['url_content']))} bytes")

        # Optional: Save results to file
        output_file = f"serper_results_{target_url.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")

    except SerperAPIError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
