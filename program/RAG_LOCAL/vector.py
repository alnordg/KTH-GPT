from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
import os
import uuid

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Path to FAISS index = faiss_index_pdf
db_location = "test4"
add_documents = not os.path.exists(db_location)

def load_documents():
    loader = PyPDFDirectoryLoader("data2")
    docs =  loader.load()
    print(docs)
    return docs  # returns list[Document]

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)  # returns list[Document]

if add_documents:
    print("creating vector db")

    # Load -> split
    loaded_documents = load_documents()
    chunks = split_documents(loaded_documents)

    # Build list of documents to index (don't mutate loaded_documents)
    docs_to_index = []
    for i, chunk in enumerate(chunks):
        text = chunk.page_content or ""
        if not text.strip():
            continue  # skip empty chunks

        # Preserve existing metadata and add chunk index
        metadata = dict(chunk.metadata) if getattr(chunk, "metadata", None) else {}
        metadata.setdefault("chunk_index", i)
        # If source exists add or keep it
        if "source" in metadata:
            metadata.setdefault("source", metadata["source"])

        # Create a new Document with a unique id to avoid collisions
        doc = Document(
            page_content=text,
            metadata=metadata,
            id=str(uuid.uuid4())
        )
        docs_to_index.append(doc)

    # Build FAISS index from documents
    vector_store = FAISS.from_documents(docs_to_index, embedding=embeddings)
    vector_store.save_local(db_location)

    # Print number of documents
    num_docs = len(vector_store.index_to_docstore_id)
    print(f"Number of docs: {num_docs}")

else:
    # Load existing FAISS index
    vector_store = FAISS.load_local(
        db_location,
        embeddings,
        allow_dangerous_deserialization=True
    )

    # Print number of documents
    num_docs = len(vector_store.index_to_docstore_id)
    print(f"Number of docs: {num_docs}")

# **This must be at the bottom**
retriever = vector_store.as_retriever(search_kwargs={"k": 15})
