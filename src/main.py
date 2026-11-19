import time
import uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.inference import ONNXInferenceEngine
from src.middleware import PIIMiddleware

app = FastAPI(
    title="GuardRail-Serve",
    description="Low-latency AI inference gateway with PII auditing and ONNX INT8 inference.",
    version="0.1.0",
)

pii_middleware = PIIMiddleware()
inference_engine = ONNXInferenceEngine()


class InferenceRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Input text to audit and run inference on.")


class InferenceResponse(BaseModel):
    request_id: str
    masked_prompt: str
    redacted_count: int
    latency_ms: float
    result: dict


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "GuardRail-Serve"}


@app.post("/infer", response_model=InferenceResponse)
def run_inference(payload: InferenceRequest) -> InferenceResponse:
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    masked_text, redacted_count = pii_middleware.mask_pii(payload.prompt)
    prediction = inference_engine.predict(masked_text)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return InferenceResponse(
        request_id=request_id,
        masked_prompt=masked_text,
        redacted_count=redacted_count,
        latency_ms=latency_ms,
        result=prediction,
    )