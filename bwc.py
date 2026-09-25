import json
import argparse
import re
import tldextract

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
    except KeyError:
        print("Looks like there's no password history for this entry")


def is_web_uri(value):
    """ Check if URL is WEB """
    match = re.match(r"^([a-z][a-z0-9+.-]*)\\?:", value, re.IGNORECASE)
    scheme = match.group(1).lower() if match else ""
    return scheme in ("", "http", "https")


def fix_domain_links():
    try:
        for uri in item["login"]["uris"]:
            value = uri["uri"]
            if not is_web_uri(value):
                continue

            extracted = tldextract.extract(value)
            # print(extracted)
            if args.domain:
                if len(extracted.suffix) == 0:
                    if args.bypassip is False:
                        # If this is IP (assume there's no suffix and domain)
                        uri.update({"uri": f'https://{extracted.domain}/'})
                else:
                    # If no subdomain
                    uri.update({"uri": f'https://{extracted.domain}.{extracted.suffix}/'})
            elif args.subdomain:
                if len(extracted.subdomain) > 0:
                    if extracted.subdomain == 'www':
                        uri.update({"uri": f'https://{extracted.domain}.{extracted.suffix}/'})
                    else:
                        uri.update({"uri": f'https://{extracted.subdomain}.{extracted.domain}.{extracted.suffix}/'})
                elif len(extracted.suffix) == 0:
                    if args.bypassip is False:
                        # If this is IP (assume there's no suffix and domain)
                        uri.update({"uri": f'https://{extracted.domain}/'})
                else:
                    # If no subdomain
                    uri.update({"uri": f'https://{extracted.domain}.{extracted.suffix}/'})
    except KeyError:
        print("No logins for this entry")


with open(args.file, "r", encoding="UTF-8") as bw:
    json_bw = json.loads(str(bw.read()))

for item in json_bw["items"]:
    if args.removeusedpw:
        remove_password_history()
    if args.domain or args.subdomain:
        fix_domain_links()

with open("bw_cleaned.json", "w", encoding="UTF-8") as bw:
    bw.write(json.dumps(json_bw, indent=2, ensure_ascii=False))
