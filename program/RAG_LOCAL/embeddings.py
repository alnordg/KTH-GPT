import os
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from docling_pipeline import docs_converter

import logging
from pathlib import Path
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DOCUMENTS_FILEPATH = "canvas_data"
FAISS_INDEX_DIR = "faiss_index_final"

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"}  # change to "cuda" for GPU
)

db_exists = os.path.exists(FAISS_INDEX_DIR)

# If no local store is present create one
if not db_exists:
    # Get the vector dimensions of the embedding model, FAISS needs to now the size of the vector embeddings at initlization
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    vector_store.add_documents(documents=docs_converter(Path(DOCUMENTS_FILEPATH).iterdir()))

    # persist to disk
    vector_store.save_local(FAISS_INDEX_DIR)
    print("Vector store made")

# If local store is present load it
else:
    vector_store = FAISS.load_local(
        FAISS_INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

# export retriever interface to use in retrieval chain
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20}
)