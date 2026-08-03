"""Latent projection for STRIDE."""
import torch
import torch.nn as nn


class LatentProjection(nn.Module):
    """Projects LLM hidden states into the TSFM's embedding space."""

    def __init__(self, llm_hidden_dim: int = 4096, tsfm_embedding_dim: int = 512, dropout: float = 0.1):
        super().__init__()
        self.projection = nn.Linear(llm_hidden_dim, tsfm_embedding_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, H: torch.Tensor) -> torch.Tensor:
        h_R = H.mean(dim=1)
        e_R = self.projection(h_R)
        return self.dropout(e_R)

    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    def load(self, path: str) -> None:
        self.load_state_dict(torch.load(path))
