import os
import platform
import sys


def _bootstrap_frozen_import_paths():
    """Ensure PyInstaller runtime can import local modules robustly."""
    if not getattr(sys, "frozen", False):
        return []

    bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    candidate_paths = [
        bundle_dir,
        os.path.join(bundle_dir, "src"),
    ]
    inserted = []
    for path in candidate_paths:
        if path not in sys.path:
            sys.path.insert(0, path)
            inserted.append(path)
    return inserted


_bootstrap_frozen_import_paths()


try:
    from .services import (
        ConfigManager,
        LangManager,
        LoggingService,
        PayloadCatalogService,
        PayloadCatalogNetworkError,
        SenderFactory,
        start_daemon_thread,
        validate_endpoint,
    )
    from .services.language_service import LanguageService
    from .services.app_service import (
        App,
        AppDependencies,
        dependencies,
        language_service,
        logging_service,
        ui_theme_service,
        LANG_DIR,
        _LOG_FILE,
        run_main,
        ui_font_family,
        ui_theme_tokens,
    )
    from .services.ui_theme_service import (
        BUTTON_GRID_LAYOUT,
        IP_PORT_GRID_LAYOUT,
        LAYOUT_METRICS,
        UiThemeService,
    )
except ImportError:
    from services import (
        ConfigManager,
        LangManager,
        LoggingService,
        PayloadCatalogService,
        PayloadCatalogNetworkError,
        SenderFactory,
        start_daemon_thread,
        validate_endpoint,
    )
    from services.language_service import LanguageService
    from services.app_service import (
        App,
        AppDependencies,
        dependencies,
        language_service,
        logging_service,
        ui_theme_service,
        LANG_DIR,
        _LOG_FILE,
        run_main,
        ui_font_family,
        ui_theme_tokens,
    )
    from services.ui_theme_service import (
        BUTTON_GRID_LAYOUT,
        IP_PORT_GRID_LAYOUT,
        LAYOUT_METRICS,
        UiThemeService,
    )


__all__ = [
    "App",
    "AppDependencies",
    "BUTTON_GRID_LAYOUT",
    "ConfigManager",
    "IP_PORT_GRID_LAYOUT",
    "LANG_DIR",
    "LAYOUT_METRICS",
    "LanguageService",
    "LangManager",
    "LoggingService",
    "PayloadCatalogService",
    "PayloadCatalogNetworkError",
    "SenderFactory",
    "UiThemeService",
    "_LOG_FILE",
    "_bootstrap_frozen_import_paths",
    "_ui_font_family",
    "_ui_theme_tokens",
    "dependencies",
    "language_service",
    "logging_service",
    "run_main",
    "start_daemon_thread",
    "ui_font_family",
    "ui_theme_tokens",
    "ui_theme_service",
    "validate_endpoint",
    # Backward compatibility aliases
    "DEFAULT_DEPENDENCIES",
    "DEFAULT_LANGUAGE_SERVICE",
    "DEFAULT_LOGGING_SERVICE",
    "DEFAULT_UI_THEME_SERVICE",
]


# Backward-compatible wrappers used by existing tests/callers.
def _ui_font_family(lang_code):
    return ui_font_family(lang_code, platform.system)


# Backward-compatible wrappers used by existing tests/callers.
def _ui_theme_tokens(lang_code):
    return ui_theme_tokens(lang_code, platform.system)


# Backward compatibility aliases for renamed module constants
DEFAULT_DEPENDENCIES = dependencies
DEFAULT_LANGUAGE_SERVICE = language_service
DEFAULT_LOGGING_SERVICE = logging_service
DEFAULT_UI_THEME_SERVICE = ui_theme_service


if __name__ == "__main__":
    sys.exit(run_main())
