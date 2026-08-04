"""Quantile loss for STRIDE."""
import torch
import torch.nn as nn
from typing import List, Optional


class QuantileLoss(nn.Module):
    def __init__(self, quantiles: List[float] = [0.1, 0.5, 0.9]):
        super().__init__()
        self.quantiles = torch.tensor(quantiles, dtype=torch.float32)

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor, quantiles: Optional[List[float]] = None) -> torch.Tensor:
        if quantiles is not None:
            quantiles_tensor = torch.tensor(quantiles, dtype=torch.float32)
        else:
            quantiles_tensor = self.quantiles.to(y_pred.device)
        y_true_expanded = y_true.unsqueeze(-1).expand_as(y_pred)
        errors = y_pred - y_true_expanded
        return torch.mean(torch.max(quantiles_tensor * errors, (quantiles_tensor - 1) * errors))


class MultiQuantileLoss:
    def __init__(self, quantiles: List[float] = [0.1, 0.5, 0.9], weights: Optional[List[float]] = None):
        self.quantile_loss = QuantileLoss(quantiles)
        self.weights = torch.tensor(weights) if weights is not None else None

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
        if self.weights is not None:
            losses = []
            for i, q in enumerate(self.quantile_loss.quantiles):
                q_pred = y_pred[..., i:i+1]
                loss = self.quantile_loss(q_pred, y_true, quantiles=[q.float()])
                losses.append(self.weights[i] * loss)
            return torch.stack(losses).sum()
        else:
            return self.quantile_loss(y_pred, y_true)
