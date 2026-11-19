import time
import uuid
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def playground_ui() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>GuardRail-Serve Playground</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; background: #f7f9fc; color: #1f2937; }
        .card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        h1 { margin-top: 0; font-size: 24px; }
        textarea { width: 100%; height: 110px; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 15px; box-sizing: border-box; }
        button { margin-top: 12px; padding: 10px 20px; font-size: 15px; font-weight: 600; background: #2563eb; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        button:hover { background: #1d4ed8; }
        pre { background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; margin-top: 20px; font-size: 13px; }
        .meta { margin-top: 16px; font-size: 14px; color: #475569; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>GuardRail-Serve</h1>
        <p class="meta">Enter a prompt below to test PII masking, UUID tracking, and inference.</p>
        <textarea id="promptInput" placeholder="Example: Hello Ram, my email is ram@example.com and phone is 9876543210."></textarea>
        <br />
        <button id="runBtn" onclick="runInfer()">Check Prompt</button>
        <pre id="outputBox">Response will appear here...</pre>
      </div>

      <script>
        async function runInfer() {
          const promptText = document.getElementById("promptInput").value.trim();
          const outputBox = document.getElementById("outputBox");
          const btn = document.getElementById("runBtn");

          if (!promptText) {
            outputBox.textContent = "Please enter a prompt first.";
            return;
          }

          btn.disabled = true;
          outputBox.textContent = "Processing...";

          try {
            const res = await fetch("/infer", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ prompt: promptText })
            });
            const data = await res.json();
            outputBox.textContent = JSON.stringify(data, null, 2);
          } catch (err) {
            outputBox.textContent = "Error: " + err.message;
          } finally {
            btn.disabled = false;
          }
        }
      </script>
    </body>
    </html>
    """


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