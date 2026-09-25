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


args = parser.parse_args()


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


def url_type(value):
    """ Check URL type """
    hostname = urlparse(value).hostname

    try:
        ipaddress.ip_address(hostname)
        return "ip"
    except ValueError:
        return "webpage"


def ip_get(value):
    return urlparse(value).hostname


def fix_links():
    try:
        for uri in item["login"]["uris"]:
            value = uri["uri"]

            if not scheme_type(value):
                continue
            print(f"Found URI: {value}")
            scheme = protocol_type(value)
            url_t = url_type(value)
            extracted = tldextract.extract(value)

            if args.domain:
                if args.bypassip:
                    if url_t != "ip":
                        uri.update({"uri": f'{scheme}{extracted.top_domain_under_public_suffix}/'})
                        print(f"[CHANGE] {value} -> {scheme}{extracted.top_domain_under_public_suffix}/")

                    if url_t == "ip":
                        print(f"[NOT CHANGED] {value} -> {value}")
                else:
                    if url_t == "ip":
                        ipa = ip_get(value)
                        uri.update({"uri": f'{scheme}{ipa}/'})
                        print(f"[CHANGE] {value} -> {scheme}{ipa}/")

                    if url_t == "webpage":
                        uri.update({"uri": f'{scheme}{extracted.top_domain_under_public_suffix}/'})
                        print(f"[CHANGE] {value} -> {scheme}{extracted.top_domain_under_public_suffix}/")

            if args.subdomain:
                if args.bypassip:
                    if url_t != "ip":
                        uri.update({"uri": f'{scheme}{extracted.subdomain}.{extracted.domain}.{extracted.suffix}/'})
                        print(f"[CHANGE] {value} -> {scheme}{extracted.subdomain}.{extracted.domain}.{extracted.suffix}/")

                    if url_t == "ip":
                        print(f"[NOT CHANGED] {value} -> {value}")
                else:
                    if url_t == "ip":
                        ipa = ip_get(value)
                        uri.update({"uri": f'{scheme}{ipa}/'})
                        print(f"[CHANGE] {value} -> {scheme}{ipa}/")

                    if url_t == "webpage":
                        uri.update({"uri": f'{scheme}{extracted.subdomain}.{extracted.domain}.{extracted.suffix}/'})
                        print(f"[CHANGE] {value} -> {scheme}{extracted.subdomain}.{extracted.domain}.{extracted.suffix}/")
    except KeyError as e:
        traceback.print_exc()
    finally:
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
