# Module 2 Assignment: RAG API & Data Quality Validation

Set up a Retrieval-Augmented Generation (RAG) FastAPI application, build a structured golden dataset from `knowledge.txt`, and implement automated data quality checks before testing model performance.

---

## 1. Objective & System Architecture

* **`knowledge.txt`**: Serves as the source knowledge base containing domain data (order tracking, order status, return processes, and refunds). Loaded into a Vector Database via `rag_pipeline.py`.
* **FastAPI Application (`main.py`)**: Exposes REST endpoints to trigger the RAG pipeline and generate responses using LLM configurations (e.g., Gemini).
* **Golden Dataset (`golden_dataset.json`)**: Benchmarking dataset consisting of question-and-expected-answer pairs derived directly from `knowledge.txt`.

---

## 2. Data Quality Validation Criteria

Before triggering the application endpoints, you must write functions to validate the dataset. The dataset must achieve a **95% quality threshold** across four key checks:

* **Duplicate Check**: Identify and flag identical duplicate questions within the dataset.
* **Similarity Check**: Detect semantically redundant questions to prevent overlap.
* **Empty Fields Check**: Verify that neither the `question` nor `expected_answer` field is missing or empty.
* **Consistency Check**: Ensure semantic accuracy and alignment between the question and the expected answer.

---

## 3. Implementation Workflow

### Step 1: Environment Setup
1. Create a project directory (e.g., `data_quality_POC`).
2. Configure your environment variables, including your Google API key.
3. Set up `rag_pipeline.py` to index the contents of `knowledge.txt` into your Vector Database.
4. Configure `main.py` to handle FastAPI routes, resolving any model or API key configuration errors.

### Step 2: Generate Golden Dataset
1. Construct a JSON dataset containing paired questions and ground-truth answers based on `knowledge.txt`.

### Step 3: Implement & Run Data Validation
1. Program functions enforcing the four validation criteria (Duplicates, Similarity, Empty Fields, Consistency).
2. If validation falls below the **95% threshold**, update the JSON file and rerun checks.

### Step 4: Application Testing & Metrics
1. Execute query calls against the active FastAPI endpoints using validated dataset questions.
2. Compare LLM-generated responses against the expected answers in your dataset.
3. Compute baseline metrics:
   * **Faithfulness**
   * **Answer Relevance**
   * **Correctness**



