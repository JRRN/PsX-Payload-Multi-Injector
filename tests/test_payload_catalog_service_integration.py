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
    def test_fetch_payloads_raises_error_when_response_is_not_json(self, mock_get):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("invalid json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        repository = PayloadCatalogService("https://example.com/payloads.json")

        with self.assertRaises(PayloadCatalogNetworkError):
            repository.fetch_payloads()

    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_raises_error_when_json_has_invalid_shape(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        repository = PayloadCatalogService("https://example.com/payloads.json")

        with self.assertRaises(PayloadCatalogNetworkError):
            repository.fetch_payloads()

    @patch("src.services.payload_catalog_service.requests.get")
    def test_fetch_payloads_raises_network_error_when_request_fails(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("offline")
        repository = PayloadCatalogService("https://example.com/payloads.json")

        with self.assertRaises(PayloadCatalogNetworkError):
            repository.fetch_payloads()


if __name__ == "__main__":
    unittest.main()
