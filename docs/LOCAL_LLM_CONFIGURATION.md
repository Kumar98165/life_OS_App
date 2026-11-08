# LifeOS Local LLM Configuration Guide

## 1. Runtime Specifications
The AI personal assistant is powered by **Ollama**, running as a background service on the host computer.

- **Default Base URL**: `http://localhost:11434`
- **Preferred Model**: `qwen2.5:3b`
- **Supported Fallbacks**: `llama3.2:latest`

---

## 2. Environment Configuration
The backend reads the following variables in `backend/.env` or system environment:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base endpoint of running Ollama daemon |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Target local model |
| `OLLAMA_TIMEOUT` | `60` | HTTP request timeout in seconds |
| `OLLAMA_TEMPERATURE` | `0.7` | Sampling temperature for creative/focused balance |
| `OLLAMA_MAX_TOKENS` | `1024` | Maximum completion length |

---

## 3. Health & Readiness Verification

### API Check Endpoint: `GET /api/v1/ai/health`
Checks whether Ollama is responsive and whether the configured model is installed.

#### Operational Response (`200 OK`):
```json
{
  "status": "success",
  "data": {
    "healthy": true,
    "model_available": true,
    "status": "operational",
    "model": "qwen2.5:3b",
    "available_models": ["qwen2.5:3b", "llama3.2:latest"],
    "base_url": "http://localhost:11434",
    "error": null
  }
}
```

#### Degraded / Offline Response (`503 Service Unavailable`):
```json
{
  "status": "success",
  "data": {
    "healthy": false,
    "model_available": false,
    "status": "unreachable",
    "model": "qwen2.5:3b",
    "base_url": "http://localhost:11434",
    "error": "Cannot connect to Ollama runtime at http://localhost:11434"
  }
}
```

---

## 4. Local Installation Verification
Verify your Ollama instance with PowerShell:
```powershell
# List installed models
ollama list

# Test direct model execution
ollama run qwen2.5:3b "Hello LifeOS"
```

