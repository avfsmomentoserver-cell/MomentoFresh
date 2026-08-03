"""End-to-end training and inference for STRIDE."""
from typing import List, Dict, Optional, Tuple, Any
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from .reasoning.teacher_llm import TeacherLLM
from .reasoning.student_llm import StudentLLM
from .projection.latent_projection import LatentProjection
from .projection.fusion import fuse_embeddings, FusionOperator
from .forecasting.tsfm_integration import get_tsfm_wrapper
from .forecasting.quantile_loss import QuantileLoss
import json
import os


class STRIDEDataset(Dataset):
    """Dataset for STRIDE training."""

    def __init__(self, data: List[Dict], teacher_llm: Optional[TeacherLLM] = None):
        self.data = data
        self.teacher_llm = teacher_llm

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict:
        sample = self.data[idx]
        if self.teacher_llm is not None:
            R_ref = self.teacher_llm.generate_reasoning(
                sample["X"], sample["Y"], sample["E"], sample.get("metadata")
            )
            sample["R_ref"] = R_ref
        return sample


def train_stride(
    teacher_llm: TeacherLLM,
    student_llm: StudentLLM,
    tsfm_name: str = "chronos-2.0",
    projection: Optional[LatentProjection] = None,
    train_data: Optional[List[Dict]] = None,
    epochs: int = 10,
    alpha: float = 0.5,
    beta: float = 0.5,
    learning_rate: float = 1e-4,
    batch_size: int = 8,
    device: str = "cpu",
    fusion_operator: FusionOperator = FusionOperator.PREPEND,
    embedding_dim: int = 512,
    forecast_horizon: int = 96,
    num_variates: int = 1,
) -> Tuple[StudentLLM, LatentProjection, Any]:
    tsfm = get_tsfm_wrapper(tsfm_name, embedding_dim, forecast_horizon, num_variates, device)
    if projection is None:
        projection = LatentProjection(4096, embedding_dim)
    projection.to(device)
    
    ce_loss = torch.nn.CrossEntropyLoss()
    quantile_loss = QuantileLoss()
    optimizer = optim.AdamW(list(projection.parameters()), lr=learning_rate)
    
    dataset = STRIDEDataset(train_data or [], teacher_llm)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    for epoch in range(epochs):
        for batch in dataloader:
            X_batch = [s["X"] for s in batch]
            Y_batch = torch.tensor([s["Y"] for s in batch], dtype=torch.float32).to(device)
            
            R_hat_batch = [student_llm.generate_reasoning(X) for X in X_batch]
            H_batch = [student_llm.get_hidden_states(X).to(device) for X in X_batch]
            H_tensor = torch.stack(H_batch)
            
            e_R = projection(H_tensor)
            X_tensor = torch.tensor([x for x in X_batch], dtype=torch.float32).to(device)
            E_TS = tsfm.get_embeddings(X_tensor)
            E_fused = fuse_embeddings(e_R, E_TS, fusion_operator)
            Y_hat = tsfm.decode(E_fused)
            
            q_loss = quantile_loss(Y_hat, Y_batch)
            optimizer.zero_grad()
            (beta * q_loss).backward()
            optimizer.step()
    
    return student_llm, projection, tsfm


def forecast_with_stride(
    student_llm: StudentLLM,
    tsfm_name: str = "chronos-2.0",
    projection: Optional[LatentProjection] = None,
    X: Optional[List[float]] = None,
    E: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
    fusion_operator: FusionOperator = FusionOperator.PREPEND,
    device: str = "cpu",
    embedding_dim: int = 512,
) -> Tuple[torch.Tensor, Dict]:
    tsfm = get_tsfm_wrapper(tsfm_name, embedding_dim, 96, 1, device)
    if projection is None:
        projection = LatentProjection(4096, embedding_dim)
    if X is None:
        raise ValueError("X must be provided.")
    
    R_hat = student_llm.generate_reasoning(X, metadata)
    H = student_llm.get_hidden_states(X).unsqueeze(0).to(device)
    e_R = projection(H)
    X_tensor = torch.tensor([X], dtype=torch.float32).to(device)
    E_TS = tsfm.get_embeddings(X_tensor)
    E_fused = fuse_embeddings(e_R, E_TS, fusion_operator)
    Y_hat = tsfm.decode(E_fused)
    return Y_hat, R_hat


def save_stride_model(student_llm: StudentLLM, projection: LatentProjection, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    projection.save(os.path.join(output_dir, "projection.pth"))
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump({"model_name": student_llm.model_name}, f)


def load_stride_model(student_llm: StudentLLM, projection: LatentProjection, input_dir: str) -> Tuple[StudentLLM, LatentProjection]:
    projection.load(os.path.join(input_dir, "projection.pth"))
    return student_llm, projection
