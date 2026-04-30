#!/usr/bin/env python3
"""Sync FOG Project host data to Snipe-IT.

Configuration:
  Required env vars:
    FOG_BASE_URL, FOG_API_TOKEN, FOG_USER_TOKEN, SNIPEIT_BASE_URL, SNIPEIT_API_TOKEN
  Optional env vars:
    FOG_HOSTS_ENDPOINT, VERIFY_SSL, DRY_RUN,
    SNIPEIT_DEFAULT_MODEL_ID, SNIPEIT_DEFAULT_STATUS_LABEL,
    SNIPEIT_COMPANY_NAME, SNIPEIT_CREATE_COMPANY

Example cron:
  */30 * * * * /usr/bin/env FOG_BASE_URL=https://fog.example.com \
    FOG_API_TOKEN=... FOG_USER_TOKEN=... \
    SNIPEIT_BASE_URL=https://snipe.example.com SNIPEIT_API_TOKEN=... \
    SNIPEIT_DEFAULT_MODEL_ID=1 SNIPEIT_DEFAULT_STATUS_LABEL=Deployed \
    /usr/bin/python3 /path/to/fog_to_snipeit_sync.py
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

import requests


@dataclass(frozen=True)
class FogHost:
    name: str
    asset_tag: Optional[str]
    serial: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]


@dataclass(frozen=True)
class Config:
    fog_base_url: str
    fog_api_token: str
    fog_user_token: str
    fog_hosts_endpoint: str
    snipeit_base_url: str
    snipeit_api_token: str
    snipeit_default_model_id: int
    snipeit_default_status_label: str
    snipeit_company_name: Optional[str]
    snipeit_create_company: bool
    verify_ssl: bool
    dry_run: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync FOG Project host data to Snipe-IT."
    )
    parser.add_argument("--fog-base-url", default=os.getenv("FOG_BASE_URL"))
    parser.add_argument("--fog-api-token", default=os.getenv("FOG_API_TOKEN"))
    parser.add_argument("--fog-user-token", default=os.getenv("FOG_USER_TOKEN"))
    parser.add_argument(
        "--fog-hosts-endpoint",
        default=os.getenv("FOG_HOSTS_ENDPOINT", "/fog/host"),
    )
    parser.add_argument("--snipeit-base-url", default=os.getenv("SNIPEIT_BASE_URL"))
    parser.add_argument("--snipeit-api-token", default=os.getenv("SNIPEIT_API_TOKEN"))
    parser.add_argument(
        "--snipeit-default-model-id",
        type=int,
        default=int(os.getenv("SNIPEIT_DEFAULT_MODEL_ID", "0")),
        help="Fallback model_id when FOG does not provide model data.",
    )
    parser.add_argument(
        "--snipeit-default-status-label",
        default=os.getenv("SNIPEIT_DEFAULT_STATUS_LABEL", "Deployed"),
        help="Status label name to resolve to status_id.",
    )
    parser.add_argument(
        "--snipeit-company-name",
        default=os.getenv("SNIPEIT_COMPANY_NAME", "UC"),
        help="Company name to set on assets when supported.",
    )
    parser.add_argument(
        "--snipeit-create-company",
        action=argparse.BooleanOptionalAction,
        default=os.getenv("SNIPEIT_CREATE_COMPANY", "false").lower() == "true",
        help="Create company if missing.",
    )
    parser.add_argument(
        "--verify-ssl",
        action=argparse.BooleanOptionalAction,
        default=os.getenv("VERIFY_SSL", "true").lower() == "true",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=os.getenv("DRY_RUN", "false").lower() == "true",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> Config:
    missing = [
        name
        for name, value in {
            "FOG_BASE_URL": args.fog_base_url,
            "FOG_API_TOKEN": args.fog_api_token,
            "FOG_USER_TOKEN": args.fog_user_token,
            "SNIPEIT_BASE_URL": args.snipeit_base_url,
            "SNIPEIT_API_TOKEN": args.snipeit_api_token,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing required configuration: " + ", ".join(sorted(missing))
        )

    return Config(
        fog_base_url=args.fog_base_url.rstrip("/"),
        fog_api_token=args.fog_api_token,
        fog_user_token=args.fog_user_token,
        fog_hosts_endpoint=args.fog_hosts_endpoint,
        snipeit_base_url=args.snipeit_base_url.rstrip("/"),
        snipeit_api_token=args.snipeit_api_token,
        snipeit_default_model_id=args.snipeit_default_model_id,
        snipeit_default_status_label=args.snipeit_default_status_label,
        snipeit_company_name=args.snipeit_company_name,
        snipeit_create_company=args.snipeit_create_company,
        verify_ssl=args.verify_ssl,
        dry_run=args.dry_run,
    )


def fog_headers(config: Config) -> Mapping[str, str]:
    return {
        "fog-api-token": config.fog_api_token,
        "fog-user-token": config.fog_user_token,
        "Accept": "application/json",
    }


def snipeit_headers(config: Config) -> Mapping[str, str]:
    return {
        "Authorization": f"Bearer {config.snipeit_api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def fetch_fog_hosts(config: Config) -> List[FogHost]:
    """Return host list with tag1/tag2 mapping to asset tag/serial.

    If your FOG payload differs, adjust the extraction for tag1/tag2/model/manufacturer.
    """
    url = f"{config.fog_base_url}{config.fog_hosts_endpoint}"
    response = requests.get(
        url,
        headers=fog_headers(config),
        timeout=30,
        verify=config.verify_ssl,
    )
    response.raise_for_status()
    payload = response.json()

    hosts_payload = None
    if isinstance(payload, dict):
        for key in ("hosts", "data", "hosts_payload", "host", "items"):
            if key in payload:
                hosts_payload = payload[key]
                break
    if hosts_payload is None:
        hosts_payload = payload

    if isinstance(hosts_payload, dict):
        hosts_items = hosts_payload.get("host") or hosts_payload.get("hosts")
    else:
        hosts_items = hosts_payload

    if not isinstance(hosts_items, list):
        raise ValueError("Unexpected FOG response format for hosts list")

    hosts: List[FogHost] = []
    for item in hosts_items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("hostName") or "").strip()
        asset_tag = item.get("tag1") or item.get("hostTag1")
        serial = item.get("tag2") or item.get("hostTag2")
        model = item.get("model") or item.get("hostModel")
        manufacturer = item.get("manufacturer") or item.get("hostManufacturer")

        if not name:
            continue

        hosts.append(
            FogHost(
                name=name,
                asset_tag=str(asset_tag).strip() if asset_tag else None,
                serial=str(serial).strip() if serial else None,
                model=str(model).strip() if model else None,
                manufacturer=str(manufacturer).strip() if manufacturer else None,
            )
        )
    return hosts


def snipeit_paginated_search(
    config: Config, endpoint: str, search: Optional[str] = None
) -> Iterable[Dict[str, object]]:
    offset = 0
    limit = 50
    while True:
        params: Dict[str, object] = {"offset": offset, "limit": limit}
        if search:
            params["search"] = search
        response = requests.get(
            f"{config.snipeit_base_url}{endpoint}",
            headers=snipeit_headers(config),
            params=params,
            timeout=30,
            verify=config.verify_ssl,
        )
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("rows", [])
        for row in rows:
            yield row
        if offset + limit >= payload.get("total", len(rows)):
            break
        offset += limit


def resolve_snipeit_status_id(config: Config, label: str) -> int:
    for row in snipeit_paginated_search(config, "/api/v1/statuslabels", label):
        if str(row.get("name", "")).strip().lower() == label.lower():
            return int(row["id"])
    raise ValueError(f"Status label not found in Snipe-IT: {label}")


def resolve_snipeit_company_id(config: Config, name: str) -> Optional[int]:
    if not name:
        return None
    for row in snipeit_paginated_search(config, "/api/v1/companies", name):
        if str(row.get("name", "")).strip().lower() == name.lower():
            return int(row["id"])
    if config.snipeit_create_company:
        payload = {"name": name}
        if config.dry_run:
            print(f"[DRY RUN] Would create company: {payload}")
            return None
        response = requests.post(
            f"{config.snipeit_base_url}/api/v1/companies",
            headers=snipeit_headers(config),
            json=payload,
            timeout=30,
            verify=config.verify_ssl,
        )
        response.raise_for_status()
        created = response.json()
        return int(created.get("payload", {}).get("id") or created.get("id"))
    return None


def resolve_or_create_manufacturer_id(config: Config, name: str) -> Optional[int]:
    if not name:
        return None
    for row in snipeit_paginated_search(
        config, "/api/v1/manufacturers", name
    ):
        if str(row.get("name", "")).strip().lower() == name.lower():
            return int(row["id"])
    payload = {"name": name}
    if config.dry_run:
        print(f"[DRY RUN] Would create manufacturer: {payload}")
        return None
    response = requests.post(
        f"{config.snipeit_base_url}/api/v1/manufacturers",
        headers=snipeit_headers(config),
        json=payload,
        timeout=30,
        verify=config.verify_ssl,
    )
    response.raise_for_status()
    created = response.json()
    return int(created.get("payload", {}).get("id") or created.get("id"))


def resolve_or_create_model_id(
    config: Config, manufacturer_id: Optional[int], model_name: str
) -> Optional[int]:
    if not model_name:
        return None
    for row in snipeit_paginated_search(config, "/api/v1/models", model_name):
        if str(row.get("name", "")).strip().lower() == model_name.lower():
            if manufacturer_id and row.get("manufacturer", {}).get("id"):
                if int(row["manufacturer"]["id"]) != manufacturer_id:
                    continue
            return int(row["id"])
    payload = {
        "name": model_name,
        "manufacturer_id": manufacturer_id,
    }
    if config.dry_run:
        print(f"[DRY RUN] Would create model: {payload}")
        return None
    response = requests.post(
        f"{config.snipeit_base_url}/api/v1/models",
        headers=snipeit_headers(config),
        json=payload,
        timeout=30,
        verify=config.verify_ssl,
    )
    response.raise_for_status()
    created = response.json()
    return int(created.get("payload", {}).get("id") or created.get("id"))


def find_snipeit_asset_by_serial_or_tag(
    config: Config, serial: Optional[str], asset_tag: Optional[str]
) -> Tuple[Optional[int], Optional[Dict[str, object]]]:
    if not serial and not asset_tag:
        return None, None

    for candidate in [serial, asset_tag]:
        if not candidate:
            continue
        for row in snipeit_paginated_search(
            config, "/api/v1/hardware", candidate
        ):
            if serial and row.get("serial") == serial:
                return int(row["id"]), row
            if asset_tag and row.get("asset_tag") == asset_tag:
                return int(row["id"]), row
    return None, None


def build_asset_payload(
    host: FogHost,
    model_id: int,
    status_id: int,
    company_id: Optional[int],
) -> Dict[str, object]:
    payload: Dict[str, object] = {
        "name": host.name,
        "asset_tag": host.asset_tag,
        "serial": host.serial,
        "model_id": model_id,
        "status_id": status_id,
    }
    if company_id is not None:
        payload["company_id"] = company_id
    return {key: value for key, value in payload.items() if value}


def create_or_update_asset(
    config: Config,
    host: FogHost,
    asset_id: Optional[int],
    existing: Optional[Dict[str, object]],
    payload: Dict[str, object],
) -> str:
    if config.dry_run:
        action = "update" if asset_id else "create"
        print(f"[DRY RUN] Would {action} asset for {host.name}: {payload}")
        return action

    if asset_id and existing:
        updates = {}
        for key, value in payload.items():
            if key == "company_id":
                existing_value = existing.get("company", {}).get("id")
            elif key == "model_id":
                existing_value = existing.get("model", {}).get("id")
            elif key == "status_id":
                existing_value = existing.get("status_label", {}).get("id")
            else:
                existing_value = existing.get(key)
            if value and value != existing_value:
                updates[key] = value
        if not updates:
            return "skip"
        response = requests.put(
            f"{config.snipeit_base_url}/api/v1/hardware/{asset_id}",
            headers=snipeit_headers(config),
            json=updates,
            timeout=30,
            verify=config.verify_ssl,
        )
        response.raise_for_status()
        return "update"

    response = requests.post(
        f"{config.snipeit_base_url}/api/v1/hardware",
        headers=snipeit_headers(config),
        json=payload,
        timeout=30,
        verify=config.verify_ssl,
    )
    response.raise_for_status()
    return "create"


def resolve_model_id(config: Config, host: FogHost) -> int:
    if host.model:
        manufacturer_id = resolve_or_create_manufacturer_id(
            config, host.manufacturer or ""
        )
        model_id = resolve_or_create_model_id(config, manufacturer_id, host.model)
        if model_id:
            return model_id
    if config.snipeit_default_model_id:
        return config.snipeit_default_model_id
    raise ValueError("Unable to resolve model_id for asset creation")


def sync_hosts(config: Config) -> None:
    hosts = fetch_fog_hosts(config)
    status_id = resolve_snipeit_status_id(config, config.snipeit_default_status_label)
    company_id = None
    if config.snipeit_company_name:
        company_id = resolve_snipeit_company_id(config, config.snipeit_company_name)

    summary = {"total": 0, "created": 0, "updated": 0, "skipped": 0, "failed": 0}

    for host in hosts:
        summary["total"] += 1
        if not host.serial and not host.asset_tag:
            summary["skipped"] += 1
            print(f"[SKIP] {host.name}: missing serial/tag")
            continue
        try:
            model_id = resolve_model_id(config, host)
            payload = build_asset_payload(host, model_id, status_id, company_id)
            asset_id, existing = find_snipeit_asset_by_serial_or_tag(
                config, host.serial, host.asset_tag
            )
            action = create_or_update_asset(
                config, host, asset_id, existing, payload
            )
            if action == "create":
                summary["created"] += 1
                print(f"[CREATE] {host.name}")
            elif action == "update":
                summary["updated"] += 1
                print(f"[UPDATE] {host.name}")
            else:
                summary["skipped"] += 1
                print(f"[SKIP] {host.name}: no changes")
        except Exception as exc:
            summary["failed"] += 1
            print(f"[FAIL] {host.name}: {exc}")

    print(
        "Summary: total={total} created={created} updated={updated} "
        "skipped={skipped} failed={failed}".format(**summary)
    )


def main() -> None:
    args = parse_args()
    config = build_config(args)
    try:
        sync_hosts(config)
    except requests.RequestException as exc:
        raise SystemExit(f"API request failed: {exc}") from exc


if __name__ == "__main__":
    main()
