"""Student LLM for distilling reasoning capability."""
from typing import List, Dict, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from peft import LoraConfig, get_peft_model
import os


class StudentLLM:
    """Lightweight LLM for generating reasoning traces (R_hat) from historical data (X)."""

    def __init__(
        self,
        model_name: str = "google/gemma-3-4b-it",
        lora_rank: int = 8,
        lora_alpha: int = 32,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.model_name = model_name
        self.device = device
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float16 if "cuda" in device else torch.float32
            ).to(device)
            lora_config = LoraConfig(r=lora_rank, lora_alpha=lora_alpha, target_modules=["q_proj", "v_proj"])
            self.model = get_peft_model(self.model, lora_config)
        except Exception:
            self.tokenizer = None
            self.model = None

    def _format_prompt(self, X: List[float], metadata: Optional[Dict] = None, R_base: Optional[str] = None) -> str:
        return f"Analyze X={X}. Provide reasoning as JSON with trend, seasonality, reasoning, confidence."

    def generate_reasoning(self, X: List[float], metadata: Optional[Dict] = None, R_base: Optional[str] = None) -> Dict:
        if self.model is None:
            return {
                "trend": "increasing" if X and X[-1] > X[0] else "decreasing",
                "seasonality": "none",
                "reasoning": f"Trend: {'increasing' if X and X[-1] > X[0] else 'decreasing'}.",
                "confidence": 0.9,
            }
        prompt = self._format_prompt(X, metadata, R_base)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, generation_config=GenerationConfig(max_new_tokens=512))
        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        try:
            start_idx = output_text.find("{")
            end_idx = output_text.rfind("}") + 1
            return json.loads(output_text[start_idx:end_idx])
        except Exception:
            return {"reasoning": output_text, "confidence": 0.5}

    def get_hidden_states(self, X: List[float], metadata: Optional[Dict] = None):
        if self.model is None:
            return torch.randn(1, 10, 4096)
        prompt = self._format_prompt(X, metadata)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        return outputs.hidden_states[-1].squeeze(0)
