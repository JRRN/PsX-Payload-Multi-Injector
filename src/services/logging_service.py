import logging
import os
import sys


class LoggingService:
    def __init__(self, platform_system=None):
        self.platform_system = platform_system or (lambda: "")

    def _resolve_log_file(self):
        system = self.platform_system()
        if system == "Darwin":
            log_dir = os.path.expanduser("~/Library/Logs/PS_MultiInjector")
        elif system == "Windows":
            log_dir = os.path.join(
                os.environ.get("APPDATA", os.path.expanduser("~")),
                "PS_MultiInjector",
                "Logs",
            )
        else:
            log_dir = os.path.join(
                os.path.expanduser("~"),
                ".local",
                "share",
                "PS_MultiInjector",
                "logs",
            )
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "app.log")

    def setup(self):
        log_file = self._resolve_log_file()
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        if getattr(sys, "frozen", False):
            sys.stdout = open(log_file, "a", buffering=1)
            sys.stderr = sys.stdout
        self.info(
            "Starting PS_MultiInjector (frozen=%s, platform=%s)",
            getattr(sys, "frozen", False),
            self.platform_system(),
        )
        return log_file

    def debug(self, message, *args):
        logging.debug(message, *args)

    def info(self, message, *args):
        logging.info(message, *args)

    def error(self, message, *args):
        logging.error(message, *args)

    def critical(self, message, *args):
        logging.critical(message, *args)
