# adapt_docling_to_faiss.py
from typing import Any, Dict, List, Optional
import dataclasses
import json

# your existing imports
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

# langchain imports
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# constants
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 256
FAISS_INDEX_DIR = "faiss_index"

# --- your docling conversion + chunking (unchanged) ---
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
        InputFormat.DOCX: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
        InputFormat.PPTX: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
        InputFormat.MD: PdfFormatOption(pipeline_options=PdfPipelineOptions(do_picture_description=False)),
    }
)

print("Converting document...")
read = converter.convert("data/test.pdf")
print("Document converted.")

tokenizer = HuggingFaceTokenizer(
    tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
    max_tokens=MAX_TOKENS,
)

chunker = HybridChunker(
    tokenizer=tokenizer,
    merge_peers=True,
)
chunk_iter = chunker.chunk(dl_doc=read.document)
chunks = list(chunk_iter)  # list of docling chunk objects

# --- helper: convert docling chunk -> langchain.Document ---
def _safe_primitive(x: Any) -> Any:
    """
    Convert simple nested structures to primitives that are JSON-serializable.
    Handles dataclasses, simple objects with __dict__, enums (to str), tuples/lists/dicts recursively.
    """
    if x is None:
        return None
    if isinstance(x, (str, int, float, bool)):
        return x
    if dataclasses.is_dataclass(x):
        return _safe_primitive(dataclasses.asdict(x))
    if isinstance(x, dict):
        return {k: _safe_primitive(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_safe_primitive(v) for v in x]
    # try to pull simple attributes
    if hasattr(x, "__dict__"):
        try:
            return _safe_primitive(vars(x))
        except Exception:
            return str(x)
    # fallback to string
    return str(x)

def chunk_to_langchain_doc(chunk) -> Document:
    """
    Expect chunk has:
      - chunk.text (string)
      - chunk.meta (DocMeta-like object)
    Produces a langchain.Document(page_content=..., metadata={...})
    """
    page_content = getattr(chunk, "text", None) or getattr(chunk, "page_content", "")
    meta_obj = getattr(chunk, "meta", None)

    metadata: Dict[str, Any] = {}

    # origin / filename / mimetype
    try:
        origin = getattr(meta_obj, "origin", None)
        if origin:
            metadata["filename"] = getattr(origin, "filename", None)
            metadata["mimetype"] = getattr(origin, "mimetype", None)
            # if binary_hash or uri exists:
            metadata["binary_hash"] = getattr(origin, "binary_hash", None)
            metadata["uri"] = getattr(origin, "uri", None)
    except Exception:
        pass

    # doc_items -> provenance (page_no, charspan, bbox)
    try:
        doc_items = getattr(meta_obj, "doc_items", None)
        if doc_items:
            # take first doc_item if multiple (you can modify to keep all)
            first = doc_items[0]
            prov = getattr(first, "prov", None)
            if prov:
                first_prov = prov[0]
                metadata["page_no"] = getattr(first_prov, "page_no", None)
                # charspan may be stored on Prov or DocItem, try both
                metadata["charspan"] = getattr(first_prov, "charspan", None) or getattr(first, "charspan", None)
                # bbox -> tuple (l,t,r,b)
                bbox = getattr(first_prov, "bbox", None)
                if bbox is not None:
                    try:
                        metadata["bbox"] = (bbox.l, bbox.t, bbox.r, bbox.b)
                    except Exception:
                        metadata["bbox"] = _safe_primitive(bbox)
    except Exception:
        pass

    # store the whole metadata object as a reduced JSON-safe dict under docling_meta
    try:
        metadata["docling_meta"] = _safe_primitive(meta_obj)
    except Exception:
        metadata["docling_meta"] = str(meta_obj)

    return Document(page_content=page_content, metadata=metadata)

# convert all chunks
docs_to_index: List[Document] = [chunk_to_langchain_doc(c) for c in chunks]

# --- embeddings: HuggingFaceEmbeddings wrapper ---
# If you want to run on GPU, set model_kwargs={"device": "cuda"} and ensure torch + cuda installed.
emb = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"}  # change to "cuda" for GPU
)

# --- build FAISS index from documents ---
# This will call emb.embed_documents internally.
vector_store = FAISS.from_documents(docs_to_index, embedding=emb)

# optionally persist to disk
vector_store.save_local(FAISS_INDEX_DIR)
print(f"Saved FAISS index to {FAISS_INDEX_DIR}")

# --- example: similarity search ---
query = "Who is Max Verstappen?"
k = 3
results = vector_store.similarity_search_with_score(query, k=k)
for doc, score in results:
    print("SCORE:", score)
    print("METADATA:", json.dumps(doc.metadata, indent=2))
    print("TEXT:", doc.page_content[:400])
    print("-" * 40)
