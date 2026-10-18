"""Optional local CPU inference with an open-weight Hugging Face model.

Install with: pip install -e ".[huggingface]". Review the model card and
licence first. This adapter uses local Transformers inference, not a paid
hosted endpoint. Downloads and CPU generation can be slow or memory-intensive.
"""
from __future__ import annotations
import os
from acp.providers.base import GenerationRequest, GenerationResult


class HuggingFaceLocalProvider:
    def __init__(self, model_id: str | None = None, device: str = "cpu") -> None:
        self.model_id = (model_id or os.getenv("ACP_MODEL_ID", "")).strip()
        if not self.model_id:
            raise ValueError("Set generation.model_id or ACP_MODEL_ID to a reviewed Hugging Face model ID.")
        if device != "cpu":
            raise ValueError("The initial adapter supports CPU only.")
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                'Install optional local inference dependencies with: pip install -e ".[huggingface]"'
            ) from exc
        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=False)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id, trust_remote_code=False, low_cpu_mem_usage=True
        )
        self._model.to("cpu")
        self._model.eval()

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if not request.prompt.strip():
            raise ValueError("prompt cannot be empty")
        if not 1 <= request.max_new_tokens <= 4096:
            raise ValueError("max_new_tokens must be between 1 and 4096")
        if not 0 <= request.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        encoded = self._tokenizer(request.prompt, return_tensors="pt", truncation=True)
        with self._torch.inference_mode():
            output = self._model.generate(
                **encoded,
                max_new_tokens=request.max_new_tokens,
                do_sample=request.temperature > 0,
                temperature=max(request.temperature, 1e-5),
                pad_token_id=self._tokenizer.eos_token_id,
            )
        prompt_tokens = encoded["input_ids"].shape[1]
        text = self._tokenizer.decode(output[0][prompt_tokens:], skip_special_tokens=True).strip()
        if not text:
            raise RuntimeError("Model returned empty output")
        return GenerationResult(text=text, model_id=self.model_id, provider="huggingface_local")
