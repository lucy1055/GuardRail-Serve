# GuardRail-Serve

GuardRail-Serve is a low-latency AI inference gateway with built in PII (Personally Identifiable Information) auditing. It sits between client applications and AI models to ensure every incoming request is **privacy-safe**, **fast**, and **resource-efficient** before inference takes place.

By combining a **FastAPI** gateway, **PII masking middleware**, a custom **C++17** pre-processing extension, and **ONNX Runtime with INT8 quantization**, GuardRail-Serve protects sensitive user data while delivering **2.8x higher throughput**, **62% lower memory usage**, and **38 ms p95 latency**.

## How It Works

1. **Request Arrives & Gets a Unique ID (FastAPI):**
   When a user sends text, the request first hits the **FastAPI** gateway and gets a **Unique ID (UUID)** so every response goes back to the right user.

2. **Sensitive Data Is Masked (PII Middleware):**
   Before sending the text to the AI model, middleware scans it for personal information (such as names like `"Ram"`). If found, it masks it with `[REDACTED]` to        protect user privacy.

3. **Text Is Converted Into Numbers (C++17 Pre-processing):**
   AI models work with numbers (tokens) rather than raw words. A custom **C++17** extension handles tokenization quickly without Python serialization bottlenecks.

4. **AI Model Generates the Output (ONNX Runtime + INT8):**
   Tokens are packed into tensors and passed to an **INT8 quantized model** running on **ONNX Runtime**. This reduces memory usage and delivers fast results (`38 ms`    p95 latency).

5. **Response Is Sent Back to the User:**
   The model output returns to the gateway, matches the Unique ID, and sends the final result back to the user.

## Flow Diagram
```
[Client / User Request]
          │
          ▼
┌──────────────────────────────────────────┐
│ 1. API Gateway & UUID Assignment         │
│    Tool: FastAPI (REST API)              │
└──────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│ 2. PII Auditing & Masking Middleware     │
│    Tool: PII Middleware (e.g. "Ram" ->   │
│          "[REDACTED]")                   │
└──────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│ 3. Tokenization & Tensor Prep            │
│    Tool: Custom C++17 Extension          │
│          (2.8x throughput boost)         │
└──────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│ 4. Model Inference & Math Execution      │
│    Tool: ONNX Runtime + INT8 Quantized   │
│          Model (62% less memory, 38 ms)  │
└──────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│ 5. UUID Matching & Response Delivery     │
│    Tool: FastAPI Gateway                 │
└──────────────────────────────────────────┘
          │
          ▼
[Response Sent Back to User]
```
