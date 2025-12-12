from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

import uuid
from typing import List
from langchain_core.documents import Document

import logging
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 256

# Reads document at location <filepath> and returns a list of ducling hybrid chunked langchain Documents 
def docs_converter(filepath):
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
            InputFormat.DOCX: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
            InputFormat.PPTX: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
            InputFormat.MD: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
        }
    )

    print("Converting document...")
    read = converter.convert(filepath)
    print("Document converted.")

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
        max_tokens=MAX_TOKENS,  # optional, by default derived from `tokenizer` for HF case
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,  # optional, defaults to True
    )
    chunk_iter = chunker.chunk(dl_doc=read.document)
    chunks = list(chunk_iter)
    print(f"Split into {len(chunks)} chunks")

    # Ducling doc -> langchain Document
    docs_to_index: List[Document] = [_duckling_to_langchain(c) for c in chunks]
    return docs_to_index

def _duckling_to_langchain(chunk):
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
