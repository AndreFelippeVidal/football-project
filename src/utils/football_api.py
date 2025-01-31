import requests
import logging
import time
from ratelimit import limits, sleep_and_retry
from typing import Any, Dict
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

class FootballAPIBase:
    """
    A base class for interacting with the Football API.

    Attributes:
        BASE_URL (str): The base URL for the Football API.
        HEADERS (dict): The default headers containing the API key.
        REQUESTS_LIMIT (int): The maximum number of requests allowed per minute.
        TIME_PERIOD (int): The time period (in seconds) for rate limiting.

    Methods:
        - _make_request: Makes an HTTP GET request to the API while respecting rate limits.
        - _make_paginated_request: Makes a paginated API request and retrieves all results.
    """
    BASE_URL = "https://api.football-data.org/v4"
    HEADERS = {"X-Auth-Token": API_KEY} 

    # Rate limit: 10 per minute
    REQUESTS_LIMIT = 10
    TIME_PERIOD = 60  # Segundos


    def __init__(self, token: str = None):
        """
        Initializes the FootballAPIBase instance with the provided API token or a default token.

        Args:
            token (str, optional): The API token for authenticating requests. Defaults to None.
        """
        self.base_url = self.BASE_URL
        self.headers = {"X-Auth-Token": token or self.HEADERS["X-Auth-Token"]}

    @sleep_and_retry
    @limits(calls=REQUESTS_LIMIT, period=TIME_PERIOD)
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Makes an HTTP GET request to the API while ensuring the rate limit of 10 requests per minute is respected.

        Args:
            endpoint (str): The endpoint of the API to which the request is made.
            params (dict, optional): Additional query parameters for the request. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            ValueError: If there is an authentication error (HTTP 401) or if the resource is not found (HTTP 404).
            RuntimeError: If there is a general request error.
            ValueError: If an HTTP error occurs that is not a 401, 404, or rate limit exceeded.
        """
        MAX_RETRIES = 5
        RETRY_DELAY = 6 # in seconds, (rate limit of 10 requests per minute)
        RETRY_COUNT = 0
        url = f"{self.base_url}/{endpoint}"
        while True:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 401:
                    raise ValueError("Authentication Error: Verify you API Key.") from http_err
                elif response.status_code == 404:
                    raise ValueError("Resource not found: Verify the parameters or endpoints.") from http_err
                elif response.status_code == 429: # rate limit exceeded
                    logging.warning(f"Rate limit exceeded. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                    RETRY_COUNT += 1
                    RETRY_DELAY *= 2 # exponential backoff
                else:
                    raise ValueError(f"HTTP Error: {response.status_code} - {response.text}") from http_err

            except requests.exceptions.RequestException as req_err:
                raise RuntimeError(f"Request Error: {req_err}") from req_err
            
            if RETRY_COUNT == MAX_RETRIES:
                logging.error("Max retries exceeded. Unable to make API request.")
                break


    def _make_paginated_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Makes a paginated request to the API and retrieves all results.

        Args:
            endpoint (str): The endpoint of the API to which the request is made.
            params (dict, optional): Additional query parameters for the request. Defaults to None.

        Returns:
            list: A list of all results retrieved across all pages of the paginated request.

        Example:
            all_matches = api._make_paginated_request("matches")
        """
        url = f"{self.base_url}/{endpoint}"
        all_results = []
        while url:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                all_results.extend(data.get("content", []))
                url = data.get("next") 
            except requests.exceptions.RequestException as req_err:
                print(f"Error during pagination: {req_err}")
                break
        return all_results
