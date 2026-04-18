import unittest
from unittest.mock import Mock, patch
import requests

from src.services.payload_catalog_service import PayloadCatalogService, PayloadCatalogNetworkError


class PayloadCatalogServiceIntegrationTests(unittest.TestCase):
    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_parses_json_format(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "PS5": [
                {
                    "nombre": "kstuff.elf",
                    "url": "https://example.com/kstuff.elf",
                    "puerto": 9021,
                }
            ],
            "PS4": [
                {
                    "nombre": "goldhen.bin",
                    "url": "https://example.com/goldhen.bin",
                    "puerto": 9090,
                }
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        repository = PayloadCatalogService("https://example.com/payloads.json")

        ps4_payloads, ps5_payloads = repository.fetch_payloads()

        self.assertEqual(len(ps4_payloads), 1)
        self.assertEqual(len(ps5_payloads), 1)
        self.assertEqual(ps4_payloads[0].name, "goldhen.bin")
        self.assertEqual(ps5_payloads[0].port, 9021)

    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_splits_platforms_and_uses_temp_name(
        self,
        mock_get,
    ):
        mock_response = Mock()
        mock_response.text = "\n".join(
            [
                "etaHEN 2.0b",
                (
                    "payload-name-placeholder|"
                    "https://example.com/eta.bin|9020|PS4"
                ),
                "kstuff",
                (
                    "payload-name-placeholder|"
                    "https://example.com/kstuff.bin|9021|PS5"
                ),
            ]
        )
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        repository = PayloadCatalogService("https://example.com/payloads.txt")

        ps4_payloads, ps5_payloads = repository.fetch_payloads()

        mock_get.assert_called_once_with("https://example.com/payloads.txt", timeout=10)
        mock_response.raise_for_status.assert_called_once_with()
        self.assertEqual(len(ps4_payloads), 1)
        self.assertEqual(len(ps5_payloads), 1)
        self.assertEqual(ps4_payloads[0].name, "etaHEN 2.0b")
        self.assertEqual(ps4_payloads[0].port, "9020")
        self.assertEqual(ps5_payloads[0].name, "kstuff")
        self.assertEqual(ps5_payloads[0].platform, "PS5")

    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_ignores_empty_lines(self, mock_get):
        mock_response = Mock()
        mock_response.text = (
            "\n\nitem|https://example.com/payload.bin|9020|PS4\n\n"
        )
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        repository = PayloadCatalogService("https://example.com/payloads.txt")

        ps4_payloads, ps5_payloads = repository.fetch_payloads()

        self.assertEqual(len(ps4_payloads), 1)
        self.assertEqual(len(ps5_payloads), 0)

    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_raises_network_error_when_request_fails(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("offline")
        repository = PayloadCatalogService("https://example.com/payloads.json")

        with self.assertRaises(PayloadCatalogNetworkError):
            repository.fetch_payloads()


if __name__ == "__main__":
    unittest.main()
