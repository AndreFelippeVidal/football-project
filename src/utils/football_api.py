import requests
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
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                raise ValueError("Erro de autenticação: Verifique sua chave de API.") from http_err
            elif response.status_code == 404:
                raise ValueError("Recurso não encontrado: Verifique o endpoint ou parâmetros.") from http_err
            else:
                raise ValueError(f"Erro HTTP: {response.status_code} - {response.text}") from http_err

        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"Erro na requisição: {req_err}") from req_err

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
