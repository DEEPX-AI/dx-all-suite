# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

from .utils import mkdir
from .vis import VisTable


class EngineType(Enum):
    ONNXRUNTIME = "onnxruntime"
    DXENGINE = "dxengine"


class ModelType(Enum):
    UNET = "unet"


@dataclass
class RapidTableInput:
    model_type: Optional[ModelType] = ModelType.UNET
    model_dir_or_path: Union[str, Path, None, Dict[str, str]] = None

    engine_type: Optional[EngineType] = None
    engine_cfg: dict = field(default_factory=dict)

    use_ocr: bool = True
    ocr_params: dict = field(default_factory=dict)
    use_async: bool = False  # Async 모드 사용 여부
    device_ids: Optional[list] = None
    device_lock: Any = None


@dataclass
class RapidTableOutput:
    img: Optional[np.ndarray] = None
    pred_html: Optional[str] = None
    cell_bboxes: Optional[np.ndarray] = None
    logic_points: Optional[np.ndarray] = None
    elapse: Optional[float] = None

    def vis(
        self, save_dir: Union[str, Path, None] = None, save_name: Optional[str] = None
    ) -> np.ndarray:
        vis = VisTable()

        mkdir(save_dir)
        save_html_path = Path(save_dir) / f"{save_name}.html"
        save_drawed_path = Path(save_dir) / f"{save_name}_vis.jpg"
        save_logic_points_path = Path(save_dir) / f"{save_name}_col_row_vis.jpg"

        vis_img = vis(
            self.img,
            self.pred_html,
            self.cell_bboxes,
            self.logic_points,
            save_html_path,
            save_drawed_path,
            save_logic_points_path,
        )
        return vis_img
