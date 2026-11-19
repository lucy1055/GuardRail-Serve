import os
from typing import Any, Dict, List, Optional
import numpy as np

try:
    import onnxruntime as ort
except ImportError:
    ort = None


class ONNXInferenceEngine:
    """Handles lightweight tokenization and ONNX Runtime INT8 inference."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.model_path = model_path or os.getenv("ONNX_MODEL_PATH", "models/model_int8.onnx")
        self.session = None
        self.input_name: Optional[str] = None

        if ort is not None and os.path.exists(self.model_path):
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=sess_options,
                providers=["CPUExecutionProvider"],
            )
            self.input_name = self.session.get_inputs()[0].name

    def tokenize(self, text: str) -> List[int]:
        """Converts text into integer token IDs (placeholder for C++17 tokenizer)."""
        tokens = [ord(ch) % 256 for ch in text.strip()]
        return tokens if tokens else [0]

    def predict(self, text: str) -> Dict[str, Any]:
        """Runs inference using ONNX Runtime if available, with safe fallback."""
        tokens = self.tokenize(text)
        tensor = np.array([tokens], dtype=np.int64)

        if self.session is not None and self.input_name is not None:
            # Adjust shape/dtype if your specific ONNX model expects float32 or fixed length
            outputs = self.session.run(None, {self.input_name: tensor.astype(np.float32)})
            return {
                "mode": "onnx_int8",
                "token_count": len(tokens),
                "output_shape": list(np.array(outputs[0]).shape),
                "prediction": np.array(outputs[0]).tolist(),
            }

        # Fallback response when no .onnx file is present yet
        score = round(float(np.mean(tensor)) / 255.0, 4)
        return {
            "mode": "fallback_preview",
            "token_count": len(tokens),
            "risk_score": score,
            "summary": f"Processed {len(tokens)} tokens safely.",
        }