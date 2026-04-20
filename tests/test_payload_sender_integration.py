import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.services.payload_sender import SocatSender, TCPSender


class TCPSenderIntegrationTests(unittest.TestCase):
    @patch("socket.create_connection")
    def test_tcp_sender_reads_file_and_sends_bytes(
        self,
        mock_create_connection,
    ):
        socket_mock = Mock()
        mock_create_connection.return_value.__enter__.return_value = (
            socket_mock
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.bin"
            payload_path.write_bytes(b"payload-bytes")

            sender = TCPSender()
            sender.send("192.168.1.10", 9020, str(payload_path))

        mock_create_connection.assert_called_once_with(
            ("192.168.1.10", 9020),
            timeout=5,
        )
        socket_mock.sendall.assert_called_once_with(b"payload-bytes")


class SocatSenderIntegrationTests(unittest.TestCase):
    @patch("platform.machine", return_value="x86_64")
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.Popen")
    @patch("shutil.which", return_value="/usr/bin/socat")
    @patch("os.path.exists")
    @patch("os.chmod")
    def test_socat_sender_uses_system_binary_when_cached_binary_missing(
        self,
        mock_chmod,
        mock_exists,
        mock_which,
        mock_popen,
        _mock_system,
        _mock_machine,
    ):
        def exists_side_effect(path):
            return path == "/usr/bin/socat"

        mock_exists.side_effect = exists_side_effect
        process_mock = Mock()
        process_mock.stdin = Mock()
        process_mock.returncode = 0
        process_mock.wait = Mock()
        mock_popen.return_value = process_mock

        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.bin"
            payload_path.write_bytes(b"payload-bytes")

            sender = SocatSender()
            sender.send("192.168.1.10", 9020, str(payload_path))

        mock_which.assert_called_once_with("socat")
        mock_chmod.assert_called_once_with("/usr/bin/socat", 0o755)
        mock_popen.assert_called_once_with(
            ["/usr/bin/socat", "-t", "99999999", "-", "TCP:192.168.1.10:9020"],
            stdin=unittest.mock.ANY,
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
        )
        process_mock.stdin.write.assert_called_once_with(b"payload-bytes")
        process_mock.stdin.close.assert_called_once_with()
        process_mock.wait.assert_called_once_with(timeout=30)

    @patch("platform.machine", return_value="x86_64")
    @patch("platform.system", return_value="Linux")
    @patch("shutil.which", return_value=None)
    @patch("requests.get", side_effect=Exception("download failed"))
    def test_socat_sender_raises_localized_error_when_not_resolved(
        self,
        _mock_get,
        _mock_which,
        _mock_system,
        _mock_machine,
    ):
        sender = SocatSender()

        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.bin"
            payload_path.write_bytes(b"payload-bytes")

            with self.assertRaises(Exception) as context:
                sender.send("192.168.1.10", 9020, str(payload_path))

        self.assertTrue(str(context.exception))


if __name__ == "__main__":
    unittest.main()
