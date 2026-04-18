from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import os


logger = logging.getLogger(__name__)


class PayloadSender(ABC):
    @abstractmethod
    def send(self, ip, port, payload_path):
        pass


class TCPSender(PayloadSender):
    def send(self, ip, port, payload_path):
        import socket

        logger.info("TCPSender sending payload path=%s to %s:%s", payload_path, ip, port)
        with open(payload_path, "rb") as file_obj:
            data = file_obj.read()
        with socket.create_connection((ip, port), timeout=5) as sock:
            sock.sendall(data)
        logger.info("TCPSender payload sent successfully")


@dataclass(frozen=True)
class SocatResolutionContext:
    system: str
    arch: str
    app_data_dir: str
    socat_dir: str
    base_dir: str
    settings: object


class SocatResolveStrategy(ABC):
    @abstractmethod
    def resolve(self, context):
        raise NotImplementedError


def _normalize_arch(raw_arch):
    arch = (raw_arch or "").lower()
    if arch in {"x86_64", "amd64"}:
        return "x86_64"
    if arch in {"arm64", "aarch64"}:
        return "arm64"
    return arch


def _local_candidate_paths(cache_dir, os_name, arch_name):
    import os

    suffix = ".exe" if os_name == "Windows" else ""
    candidates = []
    if os_name == "Darwin" and arch_name == "arm64":
        candidates.append(os.path.join(cache_dir, f"socat-darwin-arm64{suffix}"))
    elif os_name == "Darwin" and arch_name == "x86_64":
        candidates.append(os.path.join(cache_dir, f"socat-darwin-x86_64{suffix}"))
    elif os_name == "Linux" and arch_name == "x86_64":
        candidates.append(os.path.join(cache_dir, f"socat-linux-x86_64{suffix}"))
    elif os_name == "Windows" and arch_name == "x86_64":
        candidates.append(os.path.join(cache_dir, "socat.exe"))
    candidates.extend(
        [
            os.path.join(cache_dir, "socat.exe"),
            os.path.join(cache_dir, "socat-linux"),
            os.path.join(cache_dir, "socat-mac"),
            os.path.join(cache_dir, "socat-mac-arm"),
        ]
    )
    return list(dict.fromkeys(candidates))


class CachedSocatResolver(SocatResolveStrategy):
    def resolve(self, context):
        import os

        for candidate in _local_candidate_paths(context.socat_dir, context.system, context.arch):
            if os.path.exists(candidate):
                logger.debug("SocatSender found cached candidate %s", candidate)
                return candidate
        return None


class DownloadSocatResolver(SocatResolveStrategy):
    def resolve(self, context):
        import os
        import requests

        download_urls = {
            ("Linux", "x86_64"): context.settings.socat_linux_x64_url,
        }
        if context.settings.socat_win_url:
            download_urls[("Windows", "x86_64")] = context.settings.socat_win_url

        url = download_urls.get((context.system, context.arch))
        if not url:
            return None

        target_name = "socat.exe" if context.system == "Windows" else f"socat-{context.system.lower()}-{context.arch}"
        download_target = os.path.join(context.socat_dir, target_name)
        try:
            logger.info("SocatSender downloading socat from %s", url)
            response = requests.get(url, timeout=12)
            response.raise_for_status()
            with open(download_target, "wb") as file_obj:
                file_obj.write(response.content)
            if context.system != "Windows":
                os.chmod(download_target, 0o755)
            
            # Validate downloaded binary by checking version
            if self._validate_binary(download_target):
                logger.info("SocatSender downloaded and validated binary at %s", download_target)
                return download_target
            else:
                logger.warning("SocatSender downloaded binary failed validation, removing...")
                try:
                    os.remove(download_target)
                except Exception:
                    pass
                return None
        except Exception as exc:
            logger.warning("SocatSender download failed: %s, trying system PATH", exc)
            return None

    @staticmethod
    def _validate_binary(binary_path):
        """Validate socat binary by checking if it runs --version."""
        import subprocess
        try:
            result = subprocess.run(
                [binary_path, "--version"],
                capture_output=True,
                timeout=2,
                text=True
            )
            return result.returncode == 0
        except Exception as exc:
            logger.debug("Binary validation failed: %s", exc)
            return False


class PathSocatResolver(SocatResolveStrategy):
    def resolve(self, context):
        import os
        import shutil

        socat_exec = shutil.which("socat")
        if not socat_exec and context.system == "Windows":
            socat_exec = shutil.which("socat.exe")
        if not socat_exec:
            return None
        if context.system != "Windows":
            os.chmod(socat_exec, 0o755)
        logger.debug("SocatSender resolved from PATH: %s", socat_exec)
        return socat_exec


class SocatSender(PayloadSender):
    def __init__(self, resolvers=None, config_manager_cls=None, lang_manager_cls=None):
        self.resolvers = tuple(resolvers or [
            CachedSocatResolver(),
            DownloadSocatResolver(),
            PathSocatResolver(),
        ])
        self.config_manager_cls = config_manager_cls
        self.lang_manager_cls = lang_manager_cls

    @staticmethod
    def is_available():
        """Check if socat is available on system (cached, PATH, or downloadable)."""
        import os
        import platform
        import shutil

        system = platform.system()
        arch = _normalize_arch(platform.machine())
        
        # Check system PATH
        socat_in_path = shutil.which("socat") or shutil.which("socat.exe")
        if socat_in_path:
            logger.debug("SocatSender found in PATH: %s", socat_in_path)
            return True
        
        # Check cached binaries
        if system == "Darwin":
            app_data_base = os.path.expanduser("~/Library/Application Support")
        elif system == "Windows":
            app_data_base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            app_data_base = os.path.join(os.path.expanduser("~"), ".local", "share")
        
        socat_dir = os.path.join(app_data_base, "PS_MultiInjector", "socat")
        for candidate in _local_candidate_paths(socat_dir, system, arch):
            if os.path.exists(candidate):
                logger.debug("SocatSender found cached: %s", candidate)
                return True
        
        logger.debug("SocatSender not available on system")
        return False

    def _build_not_found_error(self, app_data_dir, base_dir):
        config_manager_cls = self.config_manager_cls
        lang_manager_cls = self.lang_manager_cls
        if config_manager_cls is None or lang_manager_cls is None:
            try:
                from .config_manager import ConfigManager as _ConfigManager
                from .lang_manager import LangManager as _LangManager
            except ImportError:
                from config_manager import ConfigManager as _ConfigManager
                from lang_manager import LangManager as _LangManager
            config_manager_cls = _ConfigManager
            lang_manager_cls = _LangManager

        lang_dir = os.path.join(base_dir, "lang")
        config_path = os.path.join(app_data_dir, "config.ini")
        config = config_manager_cls(config_path)
        lang = lang_manager_cls(lang_dir, config.get_language())
        return Exception(lang.t("socat_not_found"))

    def _resolve_socat_exec(self, context):
        for resolver in self.resolvers:
            executable = resolver.resolve(context)
            if executable:
                return executable
        return None

    def send(self, ip, port, payload_path):
        import os
        import platform
        import subprocess
        import sys

        logger.info("SocatSender sending payload path=%s to %s:%s (PS4/PS5)", payload_path, ip, port)

        try:
            from ..models.settings import settings
        except ImportError:
            try:
                from models.settings import settings
            except ImportError:
                class _FallbackSettings:
                    socat_win_url = ""
                    socat_linux_x64_url = (
                        "https://github.com/andrew-d/static-binaries/raw/master/"
                        "binaries/linux/x86_64/socat"
                    )
                    socat_timeout = 30

                settings = _FallbackSettings()

        system = platform.system()
        if system == "Darwin":
            app_data_base = os.path.expanduser("~/Library/Application Support")
        elif system == "Windows":
            app_data_base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            app_data_base = os.path.join(os.path.expanduser("~"), ".local", "share")
        app_data_dir = os.path.join(app_data_base, "PS_MultiInjector")
        socat_dir = os.path.join(app_data_dir, "socat")
        os.makedirs(socat_dir, exist_ok=True)
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))

        arch = _normalize_arch(platform.machine())
        logger.debug("SocatSender platform=%s arch=%s", system, arch)

        context = SocatResolutionContext(
            system=system,
            arch=arch,
            app_data_dir=app_data_dir,
            socat_dir=socat_dir,
            base_dir=base_dir,
            settings=settings,
        )
        socat_exec = self._resolve_socat_exec(context)
        if not socat_exec or not os.path.exists(socat_exec):
            raise self._build_not_found_error(app_data_dir, base_dir)
        
        timeout = getattr(settings, 'socat_timeout', 30)
        with open(payload_path, "rb") as file_obj:
            proc = subprocess.Popen(
                [socat_exec, "-t", "99999999", "-", f"TCP:{ip}:{port}"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.stdin.write(file_obj.read())
            proc.stdin.close()
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.error("SocatSender timeout (>%ds) sending payload to %s:%s", timeout, ip, port)
                raise Exception(f"Socat timeout: payload send exceeded {timeout} seconds")
            
            if proc.returncode != 0:
                stderr_output = proc.stderr.read().decode(errors='ignore').strip()
                logger.error(
                    "SocatSender failed with returncode=%s to %s:%s: %s",
                    proc.returncode, ip, port, stderr_output
                )
                raise Exception(f"Socat error: {stderr_output or 'Unknown error'}")
        logger.info("SocatSender payload sent successfully to %s:%s", ip, port)
