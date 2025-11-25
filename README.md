# Enkrypt AI Quickstart 🚀

Welcome! This repository contains everything you need to get started with **Enkrypt AI** – the leading AI security and compliance platform for enterprises and developers alike.

## What is Enkrypt AI?

Enkrypt AI provides enterprise-grade guardrails, policy enforcement, and red teaming capabilities to help you deploy AI applications safely and confidently. Protect your applications from prompt injections, data leaks, toxicity, and other AI risks.

## Getting Started

### Prerequisites

Before you begin, make sure you have:

- ✅ An Enkrypt AI API key ([Get one here](https://app.enkryptai.com))
- ✅ Python 3.7+ installed
- ✅ Required packages installed:
  ```bash
  pip install enkryptai_sdk requests python-dotenv
  ```

### Configuration

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Add your API key to `.env`:
   ```bash
   ENKRYPTAI_API_KEY=your_api_key_here
   ```

### Interactive Notebooks

This quickstart guide is organized as a series of interactive notebooks. Follow them in order:

1. **[1_overview.ipynb](notebooks/1_overview.ipynb)** – Introduction to Enkrypt AI and setup
2. **[2_policies.ipynb](notebooks/2_policies.ipynb)** – Creating and managing AI safety policies
3. **[3_guardrails.ipynb](notebooks/3_guardrails.ipynb)** – Implementing guardrails for your AI applications
4. **[4_endpoints.ipynb](notebooks/4_endpoints.ipynb)** – Working with Enkrypt AI endpoints
5. **[5_redteaming.ipynb](notebooks/5_redteaming.ipynb)** – Red teaming your AI systems
6. **[6_deployments.ipynb](notebooks/6_deployments.ipynb)** – Deploying to production

## Examples

The `examples/` directory contains production-ready code samples demonstrating common use cases. Each example includes both a Python script (`.py`) and an interactive notebook (`.ipynb`) version.

### 1. Prompt Injection Guardrails

**Files:** [`call_prompt_injection_gr.py`](examples/call_prompt_injection_gr.py) | [`call_prompt_injection_gr.ipynb`](examples/call_prompt_injection_gr.ipynb)

**Purpose:** Learn three different methods to call Enkrypt AI's Prompt Injection Guardrails API.

**What you'll learn:**
- Using the Enkrypt AI SDK (recommended for Python applications)
- Making direct API calls with `requests` (for custom integrations)
- Using pre-defined guardrails policies (for consistent enforcement across teams)

**Quick Start:**
```bash
# Run the Python script
python examples/call_prompt_injection_gr.py

# Or open the notebook for interactive exploration
jupyter notebook examples/call_prompt_injection_gr.ipynb
```

**Key Features:**
- ✅ Three implementation methods with code examples
- ✅ Response parsing utilities
- ✅ Error handling best practices
- ✅ Complete working examples ready to integrate

---

### 2. Batch Processing Logs

**Files:** [`call_guardrails_for_logs.py`](examples/call_guardrails_for_logs.py) | [`call_guardrails_for_logs.ipynb`](examples/call_guardrails_for_logs.ipynb)

**Purpose:** Process large batches of logs through Enkrypt AI guardrails with rate limiting and error handling.

**What you'll learn:**
- Batch API usage for processing multiple texts efficiently
- Exponential backoff for handling rate limits (429 errors)
- Processing logs from JSON files
- Saving results in structured formats

**Quick Start:**
```bash
# Ensure you have a logs.json file (see examples/data/sample_logs.json for format)
# Update ENKRYPTAI_GUARDRAILS_NAME in the script with your policy name
python examples/call_guardrails_for_logs.py
```

**Configuration:**
- Set `BATCH_SIZE` to control how many logs are processed per API call
- Configure `ENKRYPTAI_GUARDRAILS_NAME` with your guardrails policy name
- Results are saved to `guardrails_results.json`

**Key Features:**
- ✅ Automatic batching for large datasets
- ✅ Rate limit handling with exponential backoff
- ✅ Progress tracking and error reporting
- ✅ Structured output format

---

### 3. Benchmarking Guardrails Performance

**Files:** [`benchmark_prompt_injection_gr.py`](examples/benchmark_prompt_injection_gr.py)

**Purpose:** Evaluate Enkrypt AI guardrails against standard prompt injection datasets with comprehensive metrics.

**What you'll learn:**
- Loading datasets from HuggingFace
- Calculating accuracy, precision, recall, and F1 scores
- Measuring latency statistics
- Generating detailed benchmark reports

**Quick Start:**
```bash
# Set HF_TOKEN in your .env file for HuggingFace datasets
# Run the benchmark (defaults to 100 samples from GuardrailsAI/detect-jailbreak)
python examples/benchmark_prompt_injection_gr.py
```

**Configuration:**
- `DATASET_SIZE`: Number of samples to test (default: 100)
- `DATASET_NAME`: HuggingFace dataset name (default: "GuardrailsAI/detect-jailbreak")
- `DATASET_ADAPTER_NAME`: Optional adapter name for custom formats

**Supported Dataset Formats:**
- `text` + `label` (string: "jailbreak" or "benign")
- `prompt` + `is_jailbreak` (boolean)
- `text` + `label` (integer: 0 or 1)

**Output:**
- Console display with metrics and confusion matrix
- `benchmark_results_[timestamp].json` - Summary with all metrics
- `benchmark_detailed_results_[timestamp].json` - Individual sample results

**Key Features:**
- ✅ Auto-detection of dataset formats
- ✅ Comprehensive performance metrics
- ✅ Latency analysis
- ✅ Detailed result tracking

---

### 4. Latency Benchmarking

**Files:** [`prompt_injection_latency_check.py`](examples/prompt_injection_latency_check.py)

**Purpose:** Measure and analyze the latency performance of Enkrypt AI guardrails across diverse prompt types.

**What you'll learn:**
- Generating diverse test prompts (100+ injection patterns)
- Measuring API response times
- Calculating latency statistics (min, max, average, median, P95)
- Network overhead adjustment

**Quick Start:**
```bash
python examples/prompt_injection_latency_check.py
```

**Output:**
- Console display with raw and adjusted latency statistics
- `latency_benchmark_results.json` - Complete latency data

**Test Coverage:**
The script tests 100 diverse prompts including:
- Direct injection attempts
- Social engineering patterns
- Obfuscated attacks (encoding, ROT13, Base64)
- Context manipulation
- Multi-step attacks
- Role-playing scenarios
- Template injection
- SQL/XSS/Command injection patterns

**Key Features:**
- ✅ Comprehensive prompt injection test suite
- ✅ Raw and network-adjusted latency metrics
- ✅ P95 percentile calculation
- ✅ Detailed latency distribution data

---

## Example Data

The `examples/data/` directory contains sample data files:

- **[sample_logs.json](examples/data/sample_logs.json)** - Sample log format for batch processing examples

## Resources

- 🌐 **Website:** [enkrypt.ai](https://enkryptai.com)
- 📅 **Book a Demo:** [Schedule a call with our team](https://enkryptai.com/request-a-demo)
- 📺 **YouTube:** [Enkrypt AI Channel](https://www.youtube.com/@enkryptai)

## Support

Questions? Reach out to our team or check our [documentation](https://docs.enkryptai.com).

---

**Ship Fast. Ship Safe. Stay Ahead.**
