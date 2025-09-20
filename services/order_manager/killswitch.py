"""Kill switch controls for emergency halts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict


@dataclass(slots=True)
class KillSwitchState:
    manual: bool = False
    drawdown: bool = False
    technical: bool = False
    regulatory: bool = False


class KillSwitch:
    def __init__(self) -> None:
        self.state = KillSwitchState()
        self.actions: list[str] = []

    def activate(self, reason: str) -> Dict[str, bool]:
        if hasattr(self.state, reason):
            setattr(self.state, reason, True)
        self.actions.append(reason)
        return self.status()

    def deactivate(self, reason: str | None = None) -> Dict[str, bool]:
        if reason and hasattr(self.state, reason):
            setattr(self.state, reason, False)
        elif reason is None:
            self.state = KillSwitchState()
        return self.status()

    def status(self) -> Dict[str, bool]:
        state_dict = asdict(self.state)
        state_dict["active"] = any(state_dict.values())
        return state_dict

    def is_active(self) -> bool:
        return any(asdict(self.state).values())


__all__ = ["KillSwitch", "KillSwitchState"]
