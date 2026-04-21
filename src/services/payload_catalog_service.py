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
        except Exception as exc:
            logger.error("Payload response is not valid JSON: %s", exc)
            raise PayloadCatalogNetworkError("Payload catalog must be valid JSON") from exc

        if not isinstance(data, dict):
            logger.error("Payload response has invalid JSON root type: %s", type(data).__name__)
            raise PayloadCatalogNetworkError("Payload catalog JSON must be an object")

        if not ("PS4" in data or "PS5" in data):
            logger.error("Payload JSON missing PS4/PS5 keys")
            raise PayloadCatalogNetworkError("Payload catalog JSON must contain PS4 or PS5 sections")

        logger.debug("Payload response parsed as JSON")
        return self._from_json(data)

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

