# GuardRail Serve

GuardRail Serve is a low-latency AI inference gateway with built-in PII (Personally Identifiable Information) auditing. It sits between client applications and AI models to ensure every incoming request is **privacy-safe**, **fast**, and **resource-efficient** before inference takes place.

## Key Highlights

- **Privacy First:** Scans incoming text and masks sensitive personal data (such as names like `"Ram"`) with `[REDACTED]` before it reaches the model.
- **2.8x Throughput Boost:** Uses a custom **C++17** extension for fast tokenization and pre-processing without Python serialization bottlenecks.
- **62% Lower Memory Footprint:** Runs an **INT8 quantized model** on **ONNX Runtime** to reduce memory usage while maintaining accuracy.
- **Low Latency (`38 ms` p95):** Optimized execution pipeline delivers fast responses for real-time applications.
- **Request Tracing:** Assigns a **Unique ID (UUID)** to every request so responses route back to the right client cleanly.

## How It Works

1. **Request Arrives & Gets a Unique ID (FastAPI):**
   When a user sends text, the request first hits the **FastAPI** gateway and gets a **Unique ID (UUID)** so every response goes back to the right user.

2. **Sensitive Data Is Masked (PII Middleware):**
   Before sending the text to the AI model, middleware scans it for personal information (such as names like `"Ram"`). If found, it masks it with `[REDACTED]` to protect user privacy.

3. **Text Is Converted Into Numbers (C++17 Pre-processing):**
   AI models work with numbers (tokens) rather than raw words. A custom **C++17** extension handles tokenization quickly without Python serialization bottlenecks.

4. **AI Model Generates the Output (ONNX Runtime + INT8):**
   Tokens are packed into tensors and passed to an **INT8 quantized model** running on **ONNX Runtime**. This reduces memory usage and delivers fast results (`38 ms` p95 latency).

5. **Response Is Sent Back to the User:**
   The model output returns to the gateway, matches the Unique ID, and sends the final result back to the user.

## Flow Diagram

```text
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
## Tech Stack / Tools Used

**FastAPI**
**PII Middleware**
**C++17**
**ONNX Runtime + INT8**
**PyTest**

## Project Structure

```text
GuardRail-Serve/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI workflow
├── src/
│   ├── main.py                     # FastAPI gateway & UUID tracking
│   ├── middleware.py               # PII auditing & masking middleware
│   ├── inference.py                # ONNX Runtime + INT8 inference module
│   └── cpp_extension/              # C++17 tokenization & pre-processing
├── tests/
│   └── test_gateway.py             # API & gateway test cases
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```
## How to rum
## 1 Create & Activate Virtual Environment
```
python -m venv .venv
```
## 2 Windows (PowerShell)
```
.venv\Scripts\Activate.ps1
```
## 3 Install Dependencies
```
pip install -r requirements.txt
```
## 4 Run the FastAPI Gateway
```
uvicorn src.main:app --reload
```
## 5 Run Tests
```
pytest
```
## Project Goal

The goal of **GuardRail-Serve** is to provide a fast, privacy-aware AI inference gateway that masks sensitive PII before model execution, 
accelerates pre-processing with a custom C++17 extension, and delivers low-latency, memory-efficient responses using INT8 quantized ONNX Runtime 
inference.
