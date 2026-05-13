"""Flow definitions with absolute paths."""

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "json"

if not DATA_DIR.exists():
    raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

FLOW_BASE_PLAN = {
    "name": "basePlan",
    "login": str(DATA_DIR / "mail.json"),
    "steps": str(DATA_DIR / "basePlan.json"),
    "download_keyword": "ZJ",
}

FLOW_REAL_TIME = {
    "name": "realTime",
    "login": str(DATA_DIR / "mail.json"),
    "steps": str(DATA_DIR / "realTimeProduction.json"),
    "download_keyword": "Real-time",
}

FLOW_LOSS_TIME = {
    "name": "lossTime",
    "login": str(DATA_DIR / "mail.json"),
    "steps": str(DATA_DIR / "lossTime.json"),
    "download_keyword": "Production",
}

FLOW_TEST = {
    "name": "test",
    "steps": str(DATA_DIR / "test.json"),
    "download_keyword": None,
}

COMMANDS = {
    "test": {
        "flows": [FLOW_TEST],
        "parallel": False,
    },
    "basePlan": {
        "flows": [FLOW_BASE_PLAN],
        "parallel": False,
    },
    "realTime": {
        "flows": [FLOW_REAL_TIME],
        "parallel": False,
    },
    "lossTime": {
        "flows": [FLOW_LOSS_TIME],
        "parallel": False,
    },
    "all": {
        "flows": [FLOW_BASE_PLAN, FLOW_REAL_TIME, FLOW_LOSS_TIME],
        "parallel": True,
        "max_workers": 3,
    },
}

__all__ = [
    "FLOW_BASE_PLAN",
    "FLOW_REAL_TIME",
    "FLOW_LOSS_TIME",
    "COMMANDS",
    "DATA_DIR",
]
