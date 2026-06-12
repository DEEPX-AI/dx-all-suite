"""Stretch Coach mini-game package (state machine + humanoid coach + classifier)."""

from .stretch_game import (
    StretchGame,
    PoseClassifier,
    HumanoidCoach,
    STAGES,
)

__all__ = ["StretchGame", "PoseClassifier", "HumanoidCoach", "STAGES"]
