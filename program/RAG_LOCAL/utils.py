from sentence_transformers import CrossEncoder
from embeddings import retriever

reranker = None

# Init reranking model to only load model once
def _initialize_reranker():
    global reranker
    if reranker is None:
        reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def get_results_rerank(question, num_returned_results):
    _initialize_reranker()

    results = retriever.invoke(question)

    # Cross-encoder takes a list of query-context pairs and returns a list of scores, one entry for each pair (high score = better)
    pairs = [[question, document.page_content] for document in results]
    scores = reranker.predict(pairs)

    # Combine results with scores -> tuples and sort based on score
    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )[:num_returned_results]

    # Extract only documents
    reranked_documents = [doc.page_content for doc, score in reranked]

    #i = 1
    #for doc in reranked_documents:
    #    print(f"Context {i}: {doc}\n")
    #    i += 1

    return reranked_documents