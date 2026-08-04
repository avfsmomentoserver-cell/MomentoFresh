"""Fusion logic for STRIDE."""
import torch
from enum import Enum


class FusionOperator(Enum):
    PREPEND = "prepend"
    ADD = "add"
    CONCAT = "concat"
    SUBSTITUTE = "substitute"


class GeneralizedFusionOperator:
    def __init__(self, operator: FusionOperator = FusionOperator.PREPEND):
        self.operator = operator

    def __call__(self, e_R: torch.Tensor, E_TS: torch.Tensor) -> torch.Tensor:
        if self.operator == FusionOperator.PREPEND:
            return self._prepend(e_R, E_TS)
        elif self.operator == FusionOperator.ADD:
            return self._add(e_R, E_TS)
        elif self.operator == FusionOperator.CONCAT:
            return self._concat(e_R, E_TS)
        elif self.operator == FusionOperator.SUBSTITUTE:
            return self._substitute(e_R, E_TS)
        else:
            raise ValueError(f"Unsupported fusion operator: {self.operator}")

    def _prepend(self, e_R: torch.Tensor, E_TS: torch.Tensor) -> torch.Tensor:
        e_R_expanded = e_R.unsqueeze(1).expand(-1, E_TS.shape[1], -1)
        return torch.cat([e_R_expanded, E_TS], dim=1)

    def _add(self, e_R: torch.Tensor, E_TS: torch.Tensor) -> torch.Tensor:
        e_R_expanded = e_R.unsqueeze(1).expand(-1, E_TS.shape[1], -1)
        return E_TS + e_R_expanded

    def _concat(self, e_R: torch.Tensor, E_TS: torch.Tensor) -> torch.Tensor:
        e_R_expanded = e_R.unsqueeze(1).expand(-1, E_TS.shape[1], -1)
        return torch.cat([e_R_expanded, E_TS], dim=-1)

    def _substitute(self, e_R: torch.Tensor, E_TS: torch.Tensor) -> torch.Tensor:
        E_fused = E_TS.clone()
        E_fused[:, 0, :] = e_R
        return E_fused


def fuse_embeddings(e_R: torch.Tensor, E_TS: torch.Tensor, operator: FusionOperator = FusionOperator.PREPEND) -> torch.Tensor:
    fusion_op = GeneralizedFusionOperator(operator)
    return fusion_op(e_R, E_TS)
