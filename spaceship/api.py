from typing import Dict, Any, Optional

import datetime
import logging

import requests


logger = logging.getLogger(__name__)

ENDPOINT = "https://spaceship.dev/api/v1/dns/records"


class SpaceShipDNSEntry:
    def __init__(
        self,
        name: str,
        record_type: str,
        ip: str,
        ttl: int,
        **kwargs
    ):
        self.name = name
        self.record_type = record_type
        self.ip = ip
        self.address = ip
        self.ttl = ttl
        # Store any other fields
        self.extra = kwargs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            name=data['name'],
            record_type=data['type'],
            ip=data['address'],
            ttl=data['ttl'],
            **{k: v for k, v in data.items() if k not in {'name', 'type', 'address', 'ttl'}}
        )

    def __repr__(self):
        return f"<SpaceShipDNSEntry name={self.name} record_type={self.record_type} address={self.ip} ttl={self.ttl}>"


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
        items = response.json()["items"]
        return { item['name']: SpaceShipDNSEntry.from_dict(item) for item in items }

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