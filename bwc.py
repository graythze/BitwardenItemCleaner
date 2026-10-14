import argparse
import difflib
import ipaddress
import json
import re
from urllib.parse import urlsplit
import time
import tldextract
from rich.console import Console
from rich.syntax import Syntax


SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.-]*):", re.IGNORECASE)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Clean and normalize URIs in a Bitwarden JSON vault export.",
        epilog=(
            "Examples:\n"
            "  python bwc.py vault.json --domain\n"
            "  python bwc.py vault.json --subdomain --bypassip\n"
            "  python bwc.py vault.json --rmusedpws\n"
            "  python bwc.py vault.json --domain --getpsl"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("file", help="Path to Bitwarden JSON vault file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-dom", "--domain", action="store_true", help="Convert URIs to domains only")
    group.add_argument("-subd", "--subdomain", action="store_true", help="Convert URIs with subdomain")

    parser.add_argument("-byp", "--bypassip", action="store_true", help="Bypass entries with IP")
    parser.add_argument("-rmpw", "--rmusedpws", action="store_true", help="Remove previously used passwords")
    parser.add_argument("-psl", "--getpsl", action="store_true", help="Get the Public Suffix List from the network")

    return parser


def create_tld_extractor(use_network):
    """Create an extractor that stays offline unless the user opts in."""
    return tldextract.TLDExtract() if use_network else tldextract.TLDExtract(suffix_list_urls=())


def remove_password_history(item):
    """Clear the password-history value on one vault item."""
    item["passwordHistory"] = None


def get_scheme(value):
    match = SCHEME_RE.match(value)
    return match.group(1).lower() if match else ""


def is_web_uri(value):
    """Return whether a URI has no scheme or an HTTP(S) scheme."""
    return get_scheme(value) in ("", "http", "https")


def split_web_uri(value):
    """Return scheme and hostname, including for a URI without a scheme."""
    scheme = get_scheme(value)
    parsed = urlsplit(value if scheme else f"//{value}")
    if not parsed.hostname:
        raise ValueError("URI has no hostname")
    return scheme, parsed.hostname


def format_host(hostname):
    """Wrap IPv6 hosts in brackets so they remain valid URI authorities."""
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return hostname
    return f"[{address.compressed}]" if address.version == 6 else address.compressed


def normalize_uri(value, mode, bypass_ip, extractor):
    """Return a normalized URI, or None when an IP should be bypassed."""
    scheme, hostname = split_web_uri(value)
    protocol = f"{scheme}://" if scheme else ""

    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        is_ip = False
    else:
        is_ip = True

    if is_ip:
        if bypass_ip:
            return None
        return f"{protocol}{format_host(hostname)}/"

    extracted = extractor(hostname)
    if mode == "domain":
        # Local and single-label hosts have no public suffix; preserve them.
        host = extracted.top_domain_under_public_suffix or hostname
    else:
        host = ".".join(
            part for part in (extracted.subdomain, extracted.domain, extracted.suffix) if part
        ) or hostname
    return f"{protocol}{host}/"


def fix_links(item, mode, bypass_ip, extractor):
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
            if not is_web_uri(value):
                continue
            print(f"Found URI: {value}")
            normalized = normalize_uri(value, mode, bypass_ip, extractor)
            if normalized is None:
                print(f"[NOT CHANGED] {value} -> {value}")
            else:
                uri["uri"] = normalized
                print(f"[CHANGE] {value} -> {normalized}")
        except ValueError as error:
            print(f"[SKIPPED] Invalid URI {value!r}: {error}")


def load_export(path):
    try:
        with open(path, "r", encoding="utf-8") as export_file:
            export = json.load(export_file)
    except OSError as error:
        raise ValueError(f"Cannot read input file: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Input file is not valid JSON: {error}") from error
    if not isinstance(export, dict):
        raise ValueError("Bitwarden export must be a JSON object")
    if not isinstance(export.get("items"), list):
        raise ValueError("Bitwarden export must contain an 'items' array")
    return export


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        json_bw = load_export(args.file)
    except ValueError as error:
        parser.error(str(error))

    with open(args.file, "r", encoding="utf-8") as source_file:
        old_content = source_file.readlines()

    extractor = create_tld_extractor(args.getpsl)
    mode = "domain" if args.domain else "subdomain"
    for index, item in enumerate(json_bw["items"]):
        if not isinstance(item, dict):
            print(f"[SKIPPED] Item at index {index} is not an object")
            continue
        item_id = item.get("id", f"index {index}")
        if item.get("type") != 1:
            print(f"Item {item_id} is not a password-type item\n")
            continue
        print(f"\nProcessing item with ID: {item_id}")
        if args.rmusedpws:
            remove_password_history(item)
        if args.domain or args.subdomain:
            fix_links(item, mode, args.bypassip, extractor)

    output_path = f"bw_cleaned{int(time.time())}.json"
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(json_bw, output_file, indent=2, ensure_ascii=False)

    new_content = json.dumps(json_bw, indent=2, ensure_ascii=False).splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_content,
        new_content,
        fromfile=args.file,
        tofile=output_path,
    )
    Console().print(Syntax("".join(diff), "diff", line_numbers=False))


if __name__ == "__main__":
    main()
