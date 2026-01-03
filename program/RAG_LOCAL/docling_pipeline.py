from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption, PowerpointFormatOption, MarkdownFormatOption
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
# For GPU Acceleration
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions

import uuid
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
    '''
    If you are planning to process a large amout of PDF documents it is highly recommended to use gpu acceleration. 
    The code will work out of the box even if you do not have CUDA, however, you might get some Warning meassages indicating that CUDA is not working and that it will default to CPU.
    If you do not have access to a NVIDIA GPU for CUDA gpu acceleration and want to avoid Warning messages comment out lines 41 - 58 and use this code instead:

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
                InputFormat.DOCX: WordFormatOption(),
                InputFormat.PPTX: PowerpointFormatOption(),
                InputFormat.MD: MarkdownFormatOption(),
            }
        )

    NOTE: The docling library currenty only supports GPU acceleration for PDF documents, however, MD and DOCX documents are processed very quickly even without it.
    '''
    pipeline_options_gpu = ThreadedPdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=AcceleratorDevice.CUDA),  # *** ADDED ***
        layout_batch_size=32,   # ***TUNED***
        ocr_batch_size=4,       # ***TUNED***
        table_batch_size=3,     # ***TUNED***
    )
    # Optionally disable OCR if not needed, OCR is used for processing pictures within PDF files
    pipeline_options_gpu.do_ocr = False  
    pipeline_options_gpu.do_picture_description = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options_gpu),
            InputFormat.DOCX: WordFormatOption(),
            InputFormat.PPTX: PowerpointFormatOption(),
            InputFormat.MD: MarkdownFormatOption(),
        }
    )

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
        max_tokens=MAX_TOKENS,  # optional, by default derived from `tokenizer` for HF case
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,  # optional, defaults to True
    )

    print("Converting documents...")
    read = converter.convert_all(filepath)
    print("Documents converted.")

    docs_to_index = []
    for doc in read:
        result = doc.document
        chunk_iter = chunker.chunk(dl_doc=result)             
        chunks = list(chunk_iter)

        # Ducling doc -> langchain Document
        docs_to_index.extend(_duckling_to_langchain(c) for c in chunks)

    print(f"Split into {len(docs_to_index)} chunks")
    return docs_to_index

def _duckling_to_langchain(chunk):
    page_content = getattr(chunk, "text", "empty chunk")
    metadata = {
        "filename": getattr(getattr(chunk.meta, "origin", None), "filename", "not available"),
        "page_number": (
            chunk.meta.doc_items[0].prov[0].page_no
            if getattr(chunk.meta, "doc_items", None)
            and len(chunk.meta.doc_items) > 0
            and getattr(chunk.meta.doc_items[0], "prov", None)
            and len(chunk.meta.doc_items[0].prov) > 0
            and hasattr(chunk.meta.doc_items[0].prov[0], "page_no")
            else "not available"
        ),
        "headings": getattr(chunk.meta, "headings", "not available"),
        "page_length": len(page_content) if page_content else 0,
    }

    # Create a new Document with a unique id to avoid collisions
    doc = Document(
        page_content=page_content,
        metadata=metadata,
        id=str(uuid.uuid4())
    )
    return doc
