"""Squat fitness-game logic for the yolo26n_pose mini-game."""
from .squat_counter import compute_angle, SquatCounter
from .game_visualizer import SquatGameVisualizer

__all__ = ["compute_angle", "SquatCounter", "SquatGameVisualizer"]
