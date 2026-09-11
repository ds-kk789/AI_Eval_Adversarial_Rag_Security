The Goal
Walk through module 2 use case setup and review RAG-based fast API endpoints and data quality validation processes.
The Discussion
Reviewing API setup: Covered triggering fast API endpoints using RAG-based code and handling model configuration errors in VS code.
Generating golden datasets: Discussed creating JSON format datasets containing questions and expected answers based on knowledge files.
Validating data quality: Outlined criteria for checking duplicates, similarity, and empty fields within the generated datasets.
The Next Steps
Create golden dataset: Participants to generate JSON dataset with questions and expected answers.
Check data quality: Participants to implement validation criteria and quality checks for the dataset.1
what does pallavika wants us to do in this module 2 assignment?
Gemini response
In the module 2 assignment, the instructions are to establish a data quality pipeline and test the RAG-based API endpoint. The workflow involves these key steps:
Generate a Golden Dataset: Create a JSON-formatted dataset that includes questions and their expected answers based on the provided knowledge/content files.1
Validate Data Quality: Write functions to enforce quality criteria on this dataset. You must implement checks for:1
Duplicates within the dataset.
Similarity between questions (to identify redundancies).
Empty fields (checking if either the question or the expected answer is missing).
Consistency between the question and the expected answer.
Application Testing: Once the dataset passes your quality checks, trigger the Fast API endpoint and analyze the system's generated responses.1
You should use the provided code (such as the main.py file) to run the application and trigger the endpoint for your queries.1
whats are the steps in the golden dataset , the 3 steps mentioned by palla
Gemini response
Pallavika outlined the following criteria to evaluate the quality of your golden dataset:1
Duplicate check: Identify if there are any duplicate questions within the dataset.1
Similarity check: Determine if questions are redundant or if multiple questions are effectively matching each other.1
Empty fields check: Verify that neither the question nor the expected answer field is missing (empty).1
Additionally, she suggested checking the consistency between the question and the expected answer to ensure the dataset's accuracy.1
what is the knowledge.txt for?
Gemini response
The knowledge.txt file serves as the knowledge base for the RAG (Retrieval-Augmented Generation) system. It contains the source content—specifically information related to order tracking, order status, return processes, and refunds—that is stored in the Vector Database.1

When a user submits a query, the system retrieves relevant information from this file via the Vector Database and provides it to the LLM to generate an accurate response.1
so how to start this project?
Gemini response
To begin the module 2 project, follow these steps as outlined in the session:

Environment Setup
Create Project Directory: Create a folder (e.g., data_quality_POC).1
Set Up Pipeline:
Implement/run your RAG pipeline script (e.g., rag_pipeline.py) to store the content of your knowledge.txt file into a Vector Database.1
Create and configure your main.py file to handle FastAPI endpoints.1
Note: Ensure your model configuration (e.g., Gemini 3.6 Flash) is correctly set in your code if you encounter configuration errors.1
API Configuration: Ensure you have your Google API key configured for the project.1
Project Workflow
Step 1: Build the Golden Dataset:
Create a JSON file containing a set of questions and their corresponding expected answers.1
This dataset must be based on the content provided in your knowledge.txt file (covering topics like order tracking, status, returns, and refunds).1
Step 2: Validate Data Quality:
Write functions to perform quality checks on your dataset.1
You must implement criteria to ensure the dataset meets a specific threshold (the goal is 95%). Mandatory checks include:1
Duplicate check: Identify redundant questions.1
Similarity/Consistency check: Verify if questions are redundant or if the question and expected answer match accurately.1
Empty fields check: Ensure no questions or expected answers are missing.1
If your dataset fails these checks, update the JSON file and re-validate.1
Step 3: Application Testing & Metrics:
Once the quality passes the threshold, trigger your FastAPI endpoint using the questions from your dataset to receive LLM responses.1
Calculate evaluation metrics (e.g., faithfulness, answer relevance, and correctness) by comparing the LLM-generated responses against your golden dataset's expected answers.1


pip install faiss-cpu
py -m pip install faiss-cpu
py -m venv aienv
cd aienv
cd scripts
activate