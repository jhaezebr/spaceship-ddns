from .api import delete_dns_entry, add_dns_entry

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
