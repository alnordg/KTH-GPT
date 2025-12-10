from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
from PyPDF2 import PdfReader  # for reading PDFs

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Path to FAISS index
db_location = "faiss_index_pdf"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    # Load PDF
    pdf_path = "test.pdf"
    reader = PdfReader(pdf_path)

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:  # skip empty pages
            document = Document(
                page_content=text,
                metadata={"page": i + 1},
                id=str(i)
            )
            documents.append(document)
            ids.append(str(i))

    # Build FAISS index from documents
    vector_store = FAISS.from_documents(documents, embedding=embeddings)
    vector_store.save_local(db_location)

else:
    # Load existing FAISS index
    vector_store = FAISS.load_local(
        db_location,
        embeddings,
        allow_dangerous_deserialization=True
    )

# **This must be at the bottom**
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
