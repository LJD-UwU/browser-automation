"""
Flow configurations - Define reusable flows and commands.

This module defines all available flows and commands that can be
orchestrated using FlowOrchestrator.
"""

from pathlib import Path
from navegador_automate import FlowDefinition


# Define individual flows
FLOW_BASE_PLAN = FlowDefinition(
    name="basePlan",
    login="steps_flows/data/json/mail.json",
    steps="steps_flows/data/json/basePlan.json",
    download_keyword="ZJ",
)

FLOW_REAL_TIME = FlowDefinition(
    name="realTime",
    login="steps_flows/data/json/mail.json",
    steps="steps_flows/data/json/realTimeProduction.json",
    download_keyword="Real-time",
)

FLOW_LOSS_TIME = FlowDefinition(
    name="lossTime",
    login="steps_flows/data/json/mail.json",
    steps="steps_flows/data/json/lossTime.json",
    download_keyword="Production",
)

# Define commands - combinations of flows with execution strategy
COMMANDS = {
    "base": {
        "flows": [FLOW_BASE_PLAN],
        "parallel": False,
    },
    "real": {
        "flows": [FLOW_REAL_TIME],
        "parallel": False,
    },
    "loss": {
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
]
