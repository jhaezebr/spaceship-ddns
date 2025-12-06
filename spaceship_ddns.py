"""
Update the DDNS record of a domain registered with spaceship
(https://www.spaceship.com/). You can get the API key and secret from
spaceship's website.
"""

import argparse
import datetime
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

ENDPOINT = "https://spaceship.dev/api/v1/dns/records"


def get_env_var(variable_name: str):
    domain = os.getenv(variable_name)

    if domain is None:
        raise ValueError(
            f"Please use the CLI arguments or set the {variable_name} "
            "environment variable"
        )

    return domain


def parse_args():
    parsers = argparse.ArgumentParser(description=__doc__)
    parsers.add_argument(
        "-d", "--domain",
        type=str,
        help="Domain to update",
        required=False,
    )
    parsers.add_argument(
        "-k", "--api-key",
        type=str,
        help="API key",
        required=False,
    )
    parsers.add_argument(
        "-s", "--api-secret",
        type=str,
        help="API secret",
        required=False,
    )
    parsers.add_argument(
        "-N", "--name",
        type=str,
        action='append',
        help="Target DNS name. Use @ for domain root. Can be specified multiple times. Can be specified by env variable SPACESHIP_DDNS_NAMES (comma seperated)",
        required=False,
    )
    parsers.add_argument(
        "-l", "--log-level",
        type=str,
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO",
        required=False,
    )
    parsers.add_argument(
        "--loop",
        type=int,
        nargs="?",
        const=300,
        help="Run indefinitely in a loop with optional delay in seconds (default: 300)",
        required=False,
    )
    args = parsers.parse_args()

    domain: str | None = args.domain
    if domain is None:
        domain = get_env_var("SPACESHIP_DDNS_DOMAIN")

    api_key: str | None = args.api_key
    if api_key is None:
        api_key = get_env_var("SPACESHIP_DDNS_API_KEY")

    api_secret: str | None = args.api_secret
    if api_secret is None:
        api_secret = get_env_var("SPACESHIP_DDNS_API_SECRET")

    names: list[str] | None = args.name
    if names is None:
        names_env = os.getenv("SPACESHIP_DDNS_NAMES")
        if names_env is None:
            raise ValueError(
                "Please use the -N/--name CLI arguments or set the "
                "SPACESHIP_DDNS_NAMES environment variable (comma-separated)"
            )
        names = [name.strip() for name in names_env.split(",")]

    log_level: str = args.log_level
    loop_delay: int | None = args.loop

    return domain, api_key, api_secret, names, log_level, loop_delay


def get_dns_entries(domain: str, api_key: str, api_secret: str):
    url = f"{ENDPOINT}/{domain}?take=500&skip=0"

    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
    }
    response = requests.get(url, headers=headers)

    response_text = response.content.decode("utf8")
    date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
    logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")

    return { item['name']: item for item in response.json()["items"]}


def delete_dns_entry(
    domain: str,
    api_key: str,
    api_secret: str,
    name: str,
    address: str,
):
    url = f"{ENDPOINT}/{domain}"

    payload = [
        {
            "type": "A",
            "name": name,
            "address": address,
        }
    ]
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "content-type": "application/json"
    }
    response = requests.delete(url, json=payload, headers=headers)

    response_text = response.content.decode("utf8")
    date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
    logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")
    logger.debug(f"Payload: {payload}")


def add_dns_entry(
    domain: str,
    api_key: str,
    api_secret: str,
    name: str,
    address: str,
):
    url = f"{ENDPOINT}/{domain}"

    payload = {
        "force": True,
        "items": [
            {
                "type": "A",
                "name": name,
                "address": address,
                "ttl": 1800,
            },
        ],
    }
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "content-type": "application/json",
    }
    response = requests.put(url, json=payload, headers=headers)

    response_text = response.content.decode("utf8")
    date = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d_%H-%M-%S")
    logger.info(f"(UTC) {date} HTTP {response.status_code} {response_text}")
    logger.debug(f"Payload: {payload}")

def update_dns_entry(
    domain: str,
    api_key: str,
    api_secret: str,
    name: str,
    old_address: str,
    new_address: str,
):
    delete_dns_entry(
        domain=domain,
        api_key=api_key,
        api_secret=api_secret,
        name=name,
        address=old_address
    )

    add_dns_entry(
        domain=domain,
        api_key=api_key,
        api_secret=api_secret,
        name=name,
        address=new_address
    )

def run_update(
    domain: str,
    api_key: str,
    api_secret: str,
    names: list[str],
):
    try:
        current_address = (
            requests
            .get("https://api.ipify.org")
            .content
            .decode("utf8")
        )
    except requests.RequestException as e:
        raise Exception("Unable to retrieve the current address") from e

    dns_entries = get_dns_entries(domain, api_key, api_secret)

    for name in names:
        if name not in dns_entries.keys():
            logger.info(f"Creating entry {name}")
            add_dns_entry(
                domain=domain,
                api_key=api_key,
                api_secret=api_secret,
                name=name,
                address=current_address,
            )
            continue

        entry = dns_entries[name]

        if entry["type"] != "A":
            logger.warning(f"{name} is not an A-record, ignoring")
            continue

        if entry["address"] == current_address:
            logger.info(f"{name}'s address is correctly configured")
            continue

        logger.info(f"Updating {name} entry to {current_address}")
        update_dns_entry(
            domain=domain,
            api_key=api_key,
            api_secret=api_secret,
            name=entry["name"],
            old_address=entry["address"],
            new_address=current_address,
        )

def main():
    domain, api_key, api_secret, names, log_level, loop_delay = parse_args()

    # Configure logging
    logging.basicConfig(level=log_level.upper())

    if loop_delay is not None:
        logger.info(f"Starting loop mode with {loop_delay} second delay")
        while True:
            run_update(domain, api_key, api_secret, names)
            logger.debug(f"Sleeping for {loop_delay} seconds")
            time.sleep(loop_delay)
    else:
        run_update(domain, api_key, api_secret, names)


if __name__ == "__main__":
    main()
