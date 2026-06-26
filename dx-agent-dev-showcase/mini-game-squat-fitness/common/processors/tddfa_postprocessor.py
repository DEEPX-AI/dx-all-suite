"""
3DDFA v2 Face Alignment Postprocessor

Processes 3DMM parameter output from 3DDFA v2 models.
Output tensor: [1, 62] containing pose/shape/expression parameters.
Reconstructs 68 2D facial landmarks using BFM (Basel Face Model) data.
"""

import numpy as np
import math
from typing import List

from ..base import IPostprocessor, PreprocessContext, FaceAlignmentResult
from ._bfm_data import load_bfm as _load_bfm


class TDDFAPostprocessor(IPostprocessor):
    """Postprocessor for 3DDFA v2 face alignment models."""
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.bfm = _load_bfm()
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceAlignmentResult]:
        if not outputs or len(outputs) == 0:
            return []
        
        raw_params = outputs[0].flatten().astype(np.float32)
        
        # Denormalize model output
        params = raw_params * self.bfm['param_std'] + self.bfm['param_mean']
        
        result = FaceAlignmentResult()
        result.params = raw_params
        
        # Parse 3DDFA v2 parameters
        R_ = params[:12].reshape(3, 4)
        R = R_[:, :3]                              # (3, 3) rotation
        offset = R_[:, 3:].reshape(3, 1)           # (3, 1) translation
        alpha_shp = params[12:52].reshape(-1, 1)   # (40, 1) shape
        alpha_exp = params[52:62].reshape(-1, 1)    # (10, 1) expression
        
        # Extract Euler angles from rotation matrix
        result.pose = self._extract_pose(R)
        
        # Reconstruct 68 landmarks using BFM
        lmks_2d = self._reconstruct_landmarks(R, offset, alpha_shp, alpha_exp, ctx)
        result.landmarks_2d = lmks_2d
        result.landmarks_3d = np.column_stack([lmks_2d, np.zeros(len(lmks_2d))])
        
        return [result]
    
    def get_model_name(self) -> str:
        return "3DDFA-v2"
    
    def _extract_pose(self, R):
        """Extract yaw, pitch, roll from 3x3 rotation matrix."""
        sy = float(np.clip(R[2, 0], -1.0, 1.0))
        pitch = math.asin(sy)
        cp = math.cos(pitch)
        if abs(cp) > 1e-6:
            yaw = math.atan2(float(R[2, 1]) / cp, float(R[2, 2]) / cp)
            roll = math.atan2(float(R[1, 0]) / cp, float(R[0, 0]) / cp)
        else:
            yaw = 0.0
            roll = math.atan2(float(-R[0, 1]), float(R[1, 1]))
        return [math.degrees(yaw), math.degrees(pitch), math.degrees(roll)]
    
    def _reconstruct_landmarks(self, R, offset, alpha_shp, alpha_exp, ctx):
        """Reconstruct 68 landmarks using BFM basis: pts3d = R @ (u + W_shp@a_shp + W_exp@a_exp) + offset."""
        bfm = self.bfm
        
        # BFM vertex reconstruction: (3, 68)
        shp_deform = np.einsum('ijk,kl->ij', bfm['w_shp_base'], alpha_shp)  # (3, 68)
        exp_deform = np.einsum('ijk,kl->ij', bfm['w_exp_base'], alpha_exp)  # (3, 68)
        vertices = bfm['u_base'] + shp_deform + exp_deform                  # (3, 68)
        
        # Project to 2D: pts3d = R @ vertices + offset
        pts3d = R @ vertices + offset  # (3, 68)
        
        # Convert to image coordinates (y-flip: BFM y-up → image y-down)
        pts3d[0, :] -= 1  # Python indexing
        pts3d[1, :] = self.input_height - pts3d[1, :]
        
        # Scale from model input space (120x120) to original image
        sx = ctx.original_width / self.input_width
        sy = ctx.original_height / self.input_height
        
        lmks = np.zeros((68, 2), dtype=np.float32)
        lmks[:, 0] = pts3d[0, :] * sx
        lmks[:, 1] = pts3d[1, :] * sy
        
        return lmks
