import logging
import re
from pathlib import Path

LOGS_DIR = Path("logs")


def start_test_log(nodeid):
    """Создать файл лога для теста и начать писать в него."""
    LOGS_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid)[-120:]
    path = LOGS_DIR / f"{safe_name}.log"

    handler = logging.FileHandler(path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    logger = logging.getLogger("student_api")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return handler, path


def stop_test_log(handler):
    logging.getLogger("student_api").removeHandler(handler)
    handler.close()
