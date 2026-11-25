# BenchmarkLab-AI

**A Text-to-SQL benchmarking framework for evaluating LLM-generated SQL queries.**

BenchmarkLab-AI evaluates how accurately Large Language Models translate natural-language questions into SQL queries. It executes generated SQL against a SQLite database and compares the results with ground-truth queries using both strict and semantic evaluation.

## Overview

BenchmarkLab-AI is designed to measure the performance of LLMs on Text-to-SQL tasks using real datasets, predefined benchmark questions, SQL execution validation, and result-based evaluation.

The framework currently supports benchmark execution, result persistence, failure diagnosis, and semantic evaluation.

## Benchmark Results

| Metric                |   Result |
| --------------------- | -------: |
| Benchmark Questions   |       20 |
| SQL Execution Success |     100% |
| Strict Accuracy       |      75% |
| Semantic Accuracy     |      90% |
| Average Latency       | \~968 ms |
| Total Tokens          |    8,833 |

### Strict vs Semantic Evaluation

- **Strict Evaluation:** Compares predicted SQL query results against ground-truth results with exact value matching, ignoring row order.
- **Semantic Evaluation:** Normalizes certain representation differences, such as date formats and age-range labels, and supports numeric tolerance.

## Features

- Natural-language-to-SQL generation
- Read-only SQL execution
- SQLite database integration
- Strict result evaluation
- Semantic result evaluation
- Model latency tracking
- Token usage tracking
- Benchmark run history
- Failure diagnosis
- JSON benchmark reports
- Dataset preprocessing and cleaning

## Tech Stack

- Python
- SQLite
- Pandas
- OpenAI-compatible API
- Groq API
- JSON
- SQL

## Datasets

### Customer Shopping Behavior

- 3,900 records
- Customer demographics
- Shopping preferences
- Purchase information
- Product and payment details

### Online Retail

- 536,641 cleaned records
- Transaction-level retail data
- Product quantities
- Prices
- Customer information
- Transaction dates

## Project Structure

```text
BenchmarkLab-AI/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── evaluation/
│   ├── ground_truth/
│   │   └── ground_truth.json
│   └── questions/
│       └── benchmark_questions.json
│
├── reports/
│   ├── full_benchmark_report.json
│   └── semantic_benchmark_report.json
│
├── src/
│   ├── benchmark/
│   ├── data_ingestion/
│   └── database/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Evaluation Methodology

The benchmark pipeline follows these steps:

1. Load a benchmark question.
2. Retrieve the relevant database schema.
3. Generate SQL using the configured LLM.
4. Execute the generated query using a read-only SQLite connection.
5. Execute the ground-truth SQL.
6. Compare the results.
7. Record accuracy, latency, token usage and execution status.
8. Generate benchmark reports.

## Current Benchmark

**Model:** `openai/gpt-oss-120b`

**Provider:** Groq API

| Dataset           | Strict Accuracy |
| ----------------- | --------------: |
| Customer Shopping |             80% |
| Online Retail     |             70% |
| Overall           |             75% |

| Evaluation        | Score |
| ----------------- | ----: |
| Strict Accuracy   |   75% |
| Semantic Accuracy |   90% |

The semantic evaluator improves evaluation by handling selected representation differences without relaxing genuine SQL result mismatches.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Piyush7797/BenchmarkLab-AI.git
cd BenchmarkLab-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit API keys or secrets.

## Running the Benchmark

Validate benchmark questions:

```bash
python -m src.benchmark.validate_questions
```

Run the full benchmark:

```bash
python -m src.benchmark.run_full_benchmark
```

Recalculate the semantic evaluation report:

```bash
python -m src.benchmark.evaluate_report_v2
```

Diagnose benchmark failures:

```bash
python -m src.benchmark.diagnose_failures
```

## Reports

The framework generates JSON reports containing benchmark performance and evaluation results.

- `reports/full_benchmark_report.json`
- `reports/semantic_benchmark_report.json`

These reports can be used for analysis, visualization and model comparison.

## Roadmap

- [ ] Interactive benchmark dashboard
- [ ] Multi-model benchmarking
- [ ] Model comparison analytics
- [ ] Custom dataset support
- [ ] Custom benchmark question management
- [ ] Benchmark export functionality
- [ ] Web-based interface
- [ ] Cloud deployment
- [ ] Expanded semantic evaluation

## Author

**Piyush Vishvakarma**

Computer Science Engineering Graduate | Aspiring Data Scientist & Machine Learning Engineer

- GitHub: [@Piyush7797](https://github.com/Piyush7797)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/piyush-vishvakrma1115/)

---

*BenchmarkLab-AI is an evolving project focused on building a practical and reproducible approach to evaluating LLM-based Text-to-SQL systems.*
