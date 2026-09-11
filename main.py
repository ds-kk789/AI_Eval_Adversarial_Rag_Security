import os

from fastapi import FastAPI
from pydantic import BaseModel

# --- Original Gemini client import (commented out) ---
# Replaced because the Gemini API quota was exhausted; answer generation
# now goes through Groq's free-tier chat API instead.
# from google import genai

from groq import Groq

from rag_pipeline import RAGPipeline
from dotenv import load_dotenv


load_dotenv()


# ------------------------------------------------------------
# GEMINI CLIENT (commented out — replaced by Groq client below)
# ------------------------------------------------------------

# client = genai.Client(
#     api_key=os.getenv("GOOGLE_API_KEY")
# )


# ------------------------------------------------------------
# GROQ CLIENT
# replaces the Gemini client above — free tier, no quota exhausted
# ------------------------------------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

GROQ_MODEL = "openai/gpt-oss-20b"


# ------------------------------------------------------------
# RAG PIPELINE
# ------------------------------------------------------------

rag = RAGPipeline(
    knowledge_file="knowledge.txt",
    index_dir="data/faiss"
)


# ------------------------------------------------------------
# FASTAPI
# ------------------------------------------------------------

app = FastAPI(
    title="E-Commerce RAG API"
)


# ------------------------------------------------------------
# REQUEST MODEL
# ------------------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "E-commerce RAG API is running"
    }


# ------------------------------------------------------------
# ASK ENDPOINT
# ------------------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question

    # --------------------------------------------------------
    # STEP 1: RETRIEVE SIMILAR CHUNKS
    # --------------------------------------------------------

    results = rag.search(
        question,
        top_k=3
    )

    # Extract retrieved text
    context = "\n\n".join(
        result["chunk"]
        for result in results
    )

    # --------------------------------------------------------
    # STEP 2: CREATE RAG PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an e-commerce customer support assistant.

Answer the user's question using ONLY the
provided context.

If the answer is not present in the context,
say:

"I don't have enough information to answer
that question."

Do not make up information.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    # --------------------------------------------------------
    # STEP 3: CALL GROQ
    # (original Gemini call commented out below — replaced because
    # the Gemini quota was exhausted)
    # --------------------------------------------------------

    # response = client.models.generate_content(
    #     model="gemini-2.5-flash",
    #     contents=prompt
    # )
    # answer = response.text

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = completion.choices[0].message.content

    # --------------------------------------------------------
    # STEP 4: RETURN RESPONSE
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": answer,
        "retrieved_context": [
            result["chunk"]
            for result in results
        ]
    }
