"""Distillation logic for STRIDE."""
from typing import List, Dict, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class CrossEntropyLoss:
    """Cross-entropy loss for reasoning distillation."""

    def __init__(self, ignore_index: int = -100):
        self.ignore_index = ignore_index

    def __call__(self, student_logits: torch.Tensor, teacher_tokens: torch.Tensor) -> torch.Tensor:
        logits_flat = student_logits.view(-1, student_logits.size(-1))
        tokens_flat = teacher_tokens.view(-1)
        return F.cross_entropy(logits_flat, tokens_flat, ignore_index=self.ignore_index)


def distill_reasoning(teacher_llm, student_llm, X: List[float], Y: List[float], E: Dict, metadata: Optional[Dict] = None) -> Dict:
    R_ref = teacher_llm.generate_reasoning(X, Y, E, metadata)
    R_hat = student_llm.generate_reasoning(X, metadata)
    return {"R_ref": R_ref, "R_hat": R_hat, "loss": None}
