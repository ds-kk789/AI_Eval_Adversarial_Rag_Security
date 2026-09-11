import os
from pathlib import Path

import faiss

from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Original Gemini embedding imports (commented out) ---
# Replaced because the Gemini API quota was exhausted; embeddings now run
# locally via sentence-transformers, which needs no API key and has no quota.
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from google import genai

# --- Local embeddings: replaces GoogleGenerativeAIEmbeddings ---
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()

# --- Original Gemini client setup (commented out) ---
# api_key = os.getenv("GOOGLE_API_KEY")
# client = genai.Client(api_key=api_key)


class RAGPipeline:

    def __init__(
        self,
        knowledge_file="knowledge.txt",
        index_dir="data/faiss"
    ):
        self.knowledge_file = Path(knowledge_file)
        self.index_dir = Path(index_dir)

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # --- Original Gemini embedding model (commented out) ---
        # replaced with local sentence-transformers embeddings — Gemini API quota exhausted
        # self.embedding_model = GoogleGenerativeAIEmbeddings(
        #     model="models/gemini-embedding-001"
        # )

        # Local embedding model (free, no API key, no quota)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.chunks = []
        self.index = None

        # Recursive Character Text Splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    # ------------------------------------------------
    # LOAD DOCUMENT
    # ------------------------------------------------

    def load_document(self):

        text = self.knowledge_file.read_text(
            encoding="utf-8"
        )

        return text

    # ------------------------------------------------
    # CREATE CHUNKS
    # ------------------------------------------------

    def create_chunks(self, text):

        chunks = self.text_splitter.split_text(text)

        return chunks

    # ------------------------------------------------
    # CREATE FAISS INDEX
    # ------------------------------------------------

    def build_index(self):

        print("Loading document...")

        text = self.load_document()

        print("Creating chunks...")

        self.chunks = self.create_chunks(text)

        print(f"Created {len(self.chunks)} chunks")

        # Create embeddings (local sentence-transformers)
        print("Creating embeddings...")

        embeddings = self.embedding_model.embed_documents(
            self.chunks
        )

        # Convert to float32
        embeddings = [
            list(map(float, embedding))
            for embedding in embeddings
        ]

        import numpy as np

        embeddings_array = np.array(
            embeddings,
            dtype="float32"
        )

        # Create FAISS index
        dimension = embeddings_array.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        # Add vectors
        self.index.add(
            embeddings_array
        )

        # Save FAISS index
        index_path = (
            self.index_dir / "index.faiss"
        )

        faiss.write_index(
            self.index,
            str(index_path)
        )

        # Save chunks
        chunks_path = (
            self.index_dir / "chunks.txt"
        )

        chunks_path.write_text(
            "\n---CHUNK---\n".join(self.chunks),
            encoding="utf-8"
        )

        print("FAISS index created successfully.")
        print(f"Total vectors: {self.index.ntotal}")

    # ------------------------------------------------
    # LOAD EXISTING INDEX
    # ------------------------------------------------

    def load_index(self):

        index_path = (
            self.index_dir / "index.faiss"
        )

        chunks_path = (
            self.index_dir / "chunks.txt"
        )

        self.index = faiss.read_index(
            str(index_path)
        )

        text = chunks_path.read_text(
            encoding="utf-8"
        )

        self.chunks = text.split(
            "\n---CHUNK---\n"
        )

        print("FAISS index loaded.")

    # ------------------------------------------------
    # SEARCH
    # ------------------------------------------------

    def search(
        self,
        question,
        top_k=3
    ):

        if self.index is None:
            self.load_index()

        # Embed the question (local sentence-transformers)
        question_embedding = (
            self.embedding_model.embed_query(
                question
            )
        )

        import numpy as np

        question_vector = np.array(
            [question_embedding],
            dtype="float32"
        )

        # Search FAISS
        distances, indices = self.index.search(
            question_vector,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index != -1:

                results.append({
                    "chunk": self.chunks[index],
                    "distance": float(distance)
                })

        return results


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    rag = RAGPipeline()

    # Build FAISS index
    rag.build_index()

    # Test question
    question = (
        "How long do I have to return a product?"
    )

    results = rag.search(
        question,
        top_k=3
    )

    print("\n==============================")
    print("QUESTION")
    print("==============================")

    print(question)

    print("\n==============================")
    print("RETRIEVED CONTEXT")
    print("==============================")

    for i, result in enumerate(results, 1):

        print(f"\n--- Result {i} ---")

        print(result["chunk"])

        print(
            "Distance:",
            result["distance"]
        )
