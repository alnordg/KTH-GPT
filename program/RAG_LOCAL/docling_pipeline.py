from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from typing import List
from utils import duckling_to_langchain
from langchain_core.documents import Document

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
    docs_to_index: List[Document] = [duckling_to_langchain(c) for c in chunks]
    return docs_to_index
