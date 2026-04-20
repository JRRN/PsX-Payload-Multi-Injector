import unittest

from src.models.payload import Payload


class PayloadTests(unittest.TestCase):
    def test_from_line_parses_valid_payload(self):
        payload = Payload.from_line(
            "etaHEN|https://example.com/payload.bin|PS4|9020"
        )

        self.assertIsNotNone(payload)
        self.assertEqual(payload.name, "etaHEN")
        self.assertEqual(payload.url, "https://example.com/payload.bin")
        self.assertEqual(payload.platform, "PS4")
        self.assertEqual(payload.port, "9020")

    def test_from_line_returns_none_for_invalid_format(self):
        self.assertIsNone(Payload.from_line("invalid-line"))

    def test_str_returns_display_format(self):
        payload = Payload(
            "etaHEN",
            "https://example.com/payload.bin",
            "PS5",
            "9021",
        )

        self.assertEqual(str(payload), "etaHEN (PS5:9021)")


if __name__ == "__main__":
    unittest.main()
