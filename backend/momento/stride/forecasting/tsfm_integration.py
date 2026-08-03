"""TSFM integration for STRIDE."""
import torch
from abc import ABC, abstractmethod
from typing import Optional


class TSFMWrapper(ABC):
    @abstractmethod
    def get_embeddings(self, X: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def decode(self, E_fused: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def forecast(self, X: torch.Tensor) -> torch.Tensor:
        pass


class Chronos2Wrapper(TSFMWrapper):
    def __init__(self, embedding_dim: int = 512, forecast_horizon: int = 96, num_variates: int = 1, device: str = "cpu"):
        self.embedding_dim = embedding_dim
        self.forecast_horizon = forecast_horizon
        self.num_variates = num_variates
        self.device = device
        self.model = None

    def get_embeddings(self, X: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = X.shape
        return torch.randn(batch_size, seq_len, self.embedding_dim).to(self.device)

    def decode(self, E_fused: torch.Tensor) -> torch.Tensor:
        batch_size = E_fused.shape[0]
        return torch.randn(batch_size, self.forecast_horizon, self.num_variates).to(self.device)

    def forecast(self, X: torch.Tensor) -> torch.Tensor:
        embeddings = self.get_embeddings(X)
        return self.decode(embeddings)


class TimerS1Wrapper(TSFMWrapper):
    def __init__(self, embedding_dim: int = 512, forecast_horizon: int = 96, num_variates: int = 1, device: str = "cpu"):
        self.embedding_dim = embedding_dim
        self.forecast_horizon = forecast_horizon
        self.num_variates = num_variates
        self.device = device
        self.model = None

    def get_embeddings(self, X: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = X.shape
        return torch.randn(batch_size, seq_len, self.embedding_dim).to(self.device)

    def decode(self, E_fused: torch.Tensor) -> torch.Tensor:
        batch_size = E_fused.shape[0]
        return torch.randn(batch_size, self.forecast_horizon, self.num_variates).to(self.device)

    def forecast(self, X: torch.Tensor) -> torch.Tensor:
        embeddings = self.get_embeddings(X)
        return self.decode(embeddings)


def get_tsfm_wrapper(model_name: str, embedding_dim: int = 512, forecast_horizon: int = 96, num_variates: int = 1, device: str = "cpu") -> TSFMWrapper:
    if "chronos" in model_name.lower():
        return Chronos2Wrapper(embedding_dim, forecast_horizon, num_variates, device)
    elif "timer" in model_name.lower():
        return TimerS1Wrapper(embedding_dim, forecast_horizon, num_variates, device)
    else:
        raise ValueError(f"Unsupported TSFM: {model_name}")
