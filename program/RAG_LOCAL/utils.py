from langchain_core.documents import Document
import uuid

def duckling_to_langchain(chunk):
    page_content = getattr(chunk, "text", "empty chunk")
    metadata = {
        "filename": chunk.meta.origin.filename,
        "page_number": chunk.meta.doc_items[0].prov[0].page_no,
        "headings": chunk.meta.headings,
        "page_length": len(page_content),
    }

    # Create a new Document with a unique id to avoid collisions
    doc = Document(
        page_content=page_content,
        metadata=metadata,
        id=str(uuid.uuid4())
    )
    return doc