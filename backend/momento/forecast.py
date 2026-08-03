"""Forecasting engine for MomentoFresh with STRIDE integration."""
from typing import List, Dict, Optional, Tuple, Any, Union
import torch
from .stride import (
    TeacherLLM, StudentLLM, LatentProjection, fuse_embeddings, FusionOperator,
    get_tsfm_wrapper, forecast_with_stride, convert_to_stride_format
)
from .store import MomentoStore


class ForecastEngine:
    """Forecasting engine with STRIDE and Momento integration."""

    def __init__(
        self,
        tsfm_name: str = "chronos-2.0",
        use_stride: bool = False,
        teacher_llm_api_key: Optional[str] = None,
        momento_endpoint: Optional[str] = None,
        momento_api_key: Optional[str] = None,
        device: str = "cpu",
    ):
        self.tsfm_name = tsfm_name
        self.use_stride = use_stride
        self.device = device
        self.momento_store = MomentoStore(momento_endpoint, momento_api_key) if momento_endpoint else None
        self.teacher_llm = TeacherLLM(api_key=teacher_llm_api_key) if use_stride else None
        self.student_llm = StudentLLM() if use_stride else None
        self.projection = LatentProjection(4096, 512) if use_stride else None

    def forecast(
        self, X: List[float], E: Optional[Dict] = None, metadata: Optional[Dict] = None,
        use_reasoning: bool = True,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, Dict]]:
        if self.use_stride and use_reasoning:
            Y_hat, R_hat = forecast_with_stride(
                self.student_llm, self.tsfm_name, self.projection, X=X, E=E,
                metadata=metadata, fusion_operator=FusionOperator.PREPEND, device=self.device
            )
            return Y_hat, R_hat
        else:
            tsfm = get_tsfm_wrapper(self.tsfm_name, 512, 96, 1, self.device)
            X_tensor = torch.tensor([X], dtype=torch.float32).to(self.device)
            return tsfm.forecast(X_tensor)

    def forecast_from_momento(self, key: str, use_reasoning: bool = True) -> Dict[str, Any]:
        if not self.momento_store:
            raise ValueError("Momento store not initialized.")
        stride_data = self.momento_store.get_stride_data(key)
        if not stride_data:
            raise ValueError(f"Data not found: {key}")
        X = stride_data["X"]
        E = stride_data.get("E", {})
        metadata = stride_data.get("metadata", {})
        if use_reasoning and self.use_stride:
            Y_hat, R_hat = self.forecast(X, E=E, metadata=metadata, use_reasoning=True)
            return {"forecast": Y_hat.tolist(), "reasoning": R_hat, "metadata": metadata}
        else:
            Y_hat = self.forecast(X, use_reasoning=False)
            return {"forecast": Y_hat.tolist(), "metadata": metadata}

    def store_and_forecast(self, key: str, raw_data: Dict[str, Any], use_reasoning: bool = True) -> Dict[str, Any]:
        if not self.momento_store:
            raise ValueError("Momento store not initialized.")
        self.momento_store.store_and_convert(key, raw_data)
        return self.forecast_from_momento(key, use_reasoning=use_reasoning)

    def train(self, train_data: List[Dict], epochs: int = 10, alpha: float = 0.5, beta: float = 0.5) -> None:
        if not self.use_stride:
            raise NotImplementedError("Training requires STRIDE.")
        from .stride.train import train_stride
        self.student_llm, self.projection, _ = train_stride(
            self.teacher_llm, self.student_llm, self.tsfm_name, self.projection,
            train_data, epochs, alpha, beta, device=self.device
        )

    def save_model(self, output_dir: str) -> None:
        if not self.use_stride:
            raise NotImplementedError("Saving requires STRIDE.")
        from .stride.train import save_stride_model
        save_stride_model(self.student_llm, self.projection, output_dir)

    def load_model(self, input_dir: str) -> None:
        if not self.use_stride:
            raise NotImplementedError("Loading requires STRIDE.")
        from .stride.train import load_stride_model
        self.student_llm, self.projection = load_stride_model(self.student_llm, self.projection, input_dir)
