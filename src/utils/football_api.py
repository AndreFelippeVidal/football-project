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
    BASE_URL = "https://api.football-data.org/v4"
    HEADERS = {"X-Auth-Token": API_KEY}  # Substitua pela sua chave

    # Limite de requisições: 10 por minuto
    REQUESTS_LIMIT = 10
    TIME_PERIOD = 60  # Segundos


    def __init__(self, token: str = None):
        self.base_url = self.BASE_URL
        self.headers = {"X-Auth-Token": token or self.HEADERS["X-Auth-Token"]}

    @sleep_and_retry
    @limits(calls=REQUESTS_LIMIT, period=TIME_PERIOD)
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz a requisição à API, garantindo que o limite de 10 requisições por minuto seja respeitado.
        """
        MAX_RETRIES = 3
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
                    raise ValueError("Erro de autenticação: Verifique sua chave de API.") from http_err
                elif response.status_code == 404:
                    raise ValueError("Recurso não encontrado: Verifique o endpoint ou parâmetros.") from http_err
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


    def _make_paginated_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz uma requisição paginada e retorna todos os resultados.
        """
        url = f"{self.base_url}/{endpoint}"
        all_results = []
        while url:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                all_results.extend(data.get("content", []))  # Ajuste se a API usar outra chave
                url = data.get("next")  # Próxima página, se disponível
            except requests.exceptions.RequestException as req_err:
                print(f"Erro durante paginação: {req_err}")
                break
        return all_results
