import logging

import requests

try:
    from ..models.payload import Payload
except ImportError:
    from models.payload import Payload


logger = logging.getLogger(__name__)


class PayloadCatalogNetworkError(Exception):
    pass


class PayloadCatalogService:
    def __init__(self, url):
        self.url = url
        logger.debug("PayloadCatalogService init url=%s", url)

    def fetch_payloads(self):
        logger.info("Fetching payload list from %s", self.url)
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch payload list: %s", exc)
            raise PayloadCatalogNetworkError(str(exc)) from exc

        try:
            data = response.json()
            if isinstance(data, dict) and ("PS4" in data or "PS5" in data):
                logger.debug("Payload response parsed as JSON")
                return self._from_json(data)
        except Exception:
            logger.debug("Payload response is not JSON format, trying legacy text")

        return self._from_legacy_text(getattr(response, "text", ""))

    def _from_json(self, data):
        ps4_payloads = []
        ps5_payloads = []

        for item in data.get("PS5", []):
            payload = Payload(
                name=item["nombre"],
                url=item["url"],
                platform="PS5",
                port=item["puerto"],
            )
            ps5_payloads.append(payload)

        for item in data.get("PS4", []):
            payload = Payload(
                name=item["nombre"],
                url=item["url"],
                platform="PS4",
                port=item["puerto"],
            )
            ps4_payloads.append(payload)

        logger.info("Loaded %d PS4 and %d PS5 payloads (json)", len(ps4_payloads), len(ps5_payloads))

        return ps4_payloads, ps5_payloads

    def _from_legacy_text(self, payloads_text):
        ps4_payloads = []
        ps5_payloads = []
        current_name = None

        for raw_line in payloads_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if "|" not in line:
                current_name = line
                continue

            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 4:
                continue

            name_token, url, port, platform = parts
            name = current_name if name_token == "payload-name-placeholder" and current_name else name_token

            payload = Payload(name=name, url=url, platform=platform, port=port)
            if platform.upper() == "PS5":
                ps5_payloads.append(payload)
            elif platform.upper() == "PS4":
                ps4_payloads.append(payload)

        logger.info("Loaded %d PS4 and %d PS5 payloads (legacy)", len(ps4_payloads), len(ps5_payloads))

        return ps4_payloads, ps5_payloads
