

# Spaceship DDNS


This is a single (dockerized) Python 3 script to update the main IP address of a domain registered with [Spaceship](https://www.spaceship.com/).

The code now uses a class-based API for all Spaceship interactions:

- `SpaceshipAPI`: Encapsulates all API operations for your domain.
- `SpaceShipDNSEntry`: Represents a DNS entry returned from the API.

Please note that it will only work for domains with less than 500 DNS records. Pagination is not handled.


## Usage


### CLI interface

To use the CLI interface you first have to install the dependencies as follows

```bash
pip install -r requirements.txt
```


Then, you can run the script using command line arguments:

```bash
python3 ./spaceship_ddns.py -d domain-name -k api-key -s api-secret -N subdomain1 -N subdomain2
# Help available with `python3 ./spaceship_ddns.py -h`
```

You can also set up the following environment variables:

- `SPACESHIP_DDNS_DOMAIN` (your domain)
- `SPACESHIP_DDNS_API_KEY` (your API key)
- `SPACESHIP_DDNS_API_SECRET` (your API secret)
- `SPACESHIP_DDNS_NAMES` (comma-separated list of DNS names to update, e.g. `@,www,api`)

#### Loop mode

To run the script indefinitely, use the `--loop` argument. You can optionally specify a delay in seconds:

```bash
# Run every 5 minutes (default)
python3 ./spaceship_ddns.py --loop
# Run every 60 seconds
python3 ./spaceship_ddns.py --loop 60
```


### Docker compose

Create a new empty .env file with the following environment variables:

```
SPACESHIP_DDNS_DOMAIN=YourDomainHere
SPACESHIP_DDNS_API_KEY=YourApiKeyHere
SPACESHIP_DDNS_API_SECRET=YourApiSecretHere
```

Then you can run the container with a single command.

```bash
docker compose up
```


## Python API usage

You can use the API directly in your own Python code:

```python
from spaceship.api import SpaceshipAPI

api = SpaceshipAPI(domain="yourdomain.com", api_key="...", api_secret="...")
entries = api.get_dns_entries()
for name, entry in entries.items():
    print(entry)  # entry is a SpaceShipDNSEntry object
```

## References

- [API docs](https://docs.spaceship.dev/#tag/DNS-records/operation/saveRecords)
