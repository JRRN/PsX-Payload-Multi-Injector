from pathlib import Path
import sys

import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Force offscreen (headless) Qt platform so tests run without a display.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def pytest_configure(config):
    """Create a single QApplication instance before any tests run."""
    try:
        from PySide6.QtWidgets import QApplication
        if QApplication.instance() is None:
            # Store on config so it isn't garbage-collected during the session.
            config._qt_app = QApplication(sys.argv[:1])
    except Exception:
        pass
