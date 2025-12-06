import datetime
import logging

import requests


logger = logging.getLogger(__name__)

ENDPOINT = "https://spaceship.dev/api/v1/dns/records"

class SpaceshipAPI:
    def __init__(self, domain: str, api_key: str, api_secret: str):
        self.domain = domain
        self.api_key = api_key
        self.api_secret = api_secret

    def get_dns_entries(self):
        url = f"{ENDPOINT}/{self.domain}?take=500&skip=0"
        headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
        }
        response = requests.get(url, headers=headers)
        response_text = response.content.decode("utf8")
        date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")
        return { item['name']: item for item in response.json()["items"]}

    def delete_dns_entry(self, name: str, ip: str):
        url = f"{ENDPOINT}/{self.domain}"
        payload = [
            {
                "type": "A",
                "name": name,
                "address": ip,
            }
        ]
        headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "content-type": "application/json"
        }
        response = requests.delete(url, json=payload, headers=headers)
        response_text = response.content.decode("utf8")
        date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")
        logger.debug(f"Payload: {payload}")

    def add_dns_entry(self, name: str, ip: str):
        url = f"{ENDPOINT}/{self.domain}"
        payload = {
            "force": True,
            "items": [
                {
                    "type": "A",
                    "name": name,
                    "address": ip,
                    "ttl": 1800,
                },
            ],
        }
        headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "content-type": "application/json",
        }
        response = requests.put(url, json=payload, headers=headers)
        response_text = response.content.decode("utf8")
        date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")
        logger.debug(f"Payload: {payload}")

    def update_dns_entry(
        self,
        name: str,
        old_ip: str,
        new_ip: str,
    ):
        self.delete_dns_entry(
            name=name,
            ip=old_ip
        )

        self.add_dns_entry(
            name=name,
            ip=new_ip
        )