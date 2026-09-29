import json
import argparse
import re
import traceback
from urllib.parse import urlparse
import tldextract
import ipaddress

parser = argparse.ArgumentParser()

parser.add_argument("file", help="Path to Bitwarden JSON file")

group = parser.add_mutually_exclusive_group()
group.add_argument("-domain", action="store_true", help="Convert URIs to domains only")
group.add_argument("-subdomain", action="store_true", help="Convert URIs with subdomain")
parser.add_argument("-bypassip", action="store_true", help="Bypass entries with IP")
parser.add_argument("-removeusedpw", action="store_true", help="Remove previously used passwords")
parser.add_argument(
    "--psl",
    action="store_true",
    help="Get the Public Suffix List from the network (default: use the bundled snapshot)",
)


args = parser.parse_args()

# Offline mode by default
if args.psl:
    tld_extractor = tldextract.TLDExtract()
else:
    tld_extractor = tldextract.TLDExtract(suffix_list_urls=())


def remove_password_history():
    try:
        item["passwordHistory"] = None
    except KeyError as e:
        traceback.print_exc()


def scheme_type(value):
    """ Check if URL is WEB """
    match = re.match(r"^([a-z][a-z0-9+.-]*)\\?:", value, re.IGNORECASE)
    scheme = match.group(1).lower() if match else ""
    return scheme in ("", "http", "https")


def protocol_type(value):
    """ Check and preserve protocol type """
    match = re.match(r"^([a-z][a-z0-9+.-]*)\\?:", value, re.IGNORECASE)
    scheme = match.group(1).lower() if match else ""

    if "https" in scheme:
        return "https://"
    elif "http" in scheme:
        return "http://"
    else:
        return ""


def normalize_uri(value, mode, bypass_ip):
    """Return a normalized URI, or None when an IP should be bypassed."""
    scheme = protocol_type(value)
    parsed = urlparse(value)
    hostname = parsed.hostname

    try:
        ipaddress.ip_address(hostname)
        url_t = "ip"
    except ValueError:
        url_t = "webpage"

    if url_t == "ip":
        if bypass_ip:
            return None
        return f"{scheme}{hostname}/"

    extracted = tld_extractor(value)
    if mode == "domain":
        host = extracted.top_domain_under_public_suffix
    else:
        host = ".".join(
            part for part in (extracted.subdomain, extracted.domain, extracted.suffix) if part
        )
    return f"{scheme}{host}/"


def fix_links():
    login = item.get("login")
    if not isinstance(login, dict):
        print("[SKIPPED] Item has no valid login data")
        return

    uris = login.get("uris")
    if not isinstance(uris, list):
        print("[SKIPPED] Item has no valid URI list")
        return

    for uri in uris:
        if not isinstance(uri, dict):
            print("[SKIPPED] URI entry is not an object")
            continue

        value = uri.get("uri")
        if not isinstance(value, str):
            print("[SKIPPED] URI is missing or is not a string")
            continue

        try:
            if not scheme_type(value):
                continue
            print(f"Found URI: {value}")
            mode = "domain" if args.domain else "subdomain"
            normalized = normalize_uri(value, mode, args.bypassip)
            if normalized is None:
                print(f"[NOT CHANGED] {value} -> {value}")
            else:
                uri.update({"uri": normalized})
                print(f"[CHANGE] {value} -> {normalized}")
        except (TypeError, ValueError, AttributeError) as error:
            print(f"[SKIPPED] Invalid URI {value!r}: {error}")

    print("\n")


with open(args.file, "r", encoding="UTF-8") as bw:
    json_bw = json.loads(str(bw.read()))

for item in json_bw["items"]:
    if item["type"] == 1:
        print(f"Processing item with ID: {item['id']}")
        if args.removeusedpw:
            remove_password_history()
        if args.domain or args.subdomain:
            fix_links()
    else:
        print(f"Item {item['id']} is not a password-type item\n")

with open("bw_cleaned.json", "w", encoding="UTF-8") as bw:
    bw.write(json.dumps(json_bw, indent=2, ensure_ascii=False))
