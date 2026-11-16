"""
LUNIQ - Lunar Intelligence & Quick Assessment

Main entry point.
Launches the graphical user interface defined in GUI.py.
"""

import sys
import logging
from pathlib import Path


# ---------------------------------------------------------
# PROJECT CONFIGURATION
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

# Ensure the project directory is available for imports.
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# ---------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("LUNIQ")


# ---------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------

def main() -> None:
    """Import and launch the GUI application."""
    logger.info("Starting LUNIQ...")
    logger.info("Project directory: %s", PROJECT_DIR)

    gui_file = PROJECT_DIR / "GUI.py"
    if not gui_file.is_file():
        logger.error("GUI.py was not found in: %s", PROJECT_DIR)
        raise SystemExit(1)

    try:
        import GUI

        # GUI.py must expose a main() or run() function.
        if callable(getattr(GUI, "main", None)):
            GUI.main()
        elif callable(getattr(GUI, "run", None)):
            GUI.run()
        else:
            raise AttributeError(
                "GUI.py must define a callable main() or run() function."
            )

    except Exception:
        logger.exception("An error occurred while starting LUNIQ.")
        raise SystemExit(1)

    logger.info("LUNIQ closed successfully.")


if __name__ == "__main__":
    main()
