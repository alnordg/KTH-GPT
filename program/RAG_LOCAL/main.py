from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from utils import get_results_rerank

model = OllamaLLM(model="llama3.2")
# 2. Answer the user’s question using only the information in the relevant context.

template = """
1. You are a highly helpful, precise assistant. Provide as much detail as you can in your answers.
2. Answer the user's question using the ONLY the provided context. 
3. If something is unclear you are allowed use the context as a guideline, explain all mentioned concepts in the context.

context:
{results}

User’s question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")
    if question == "q":
        break

    results = get_results_rerank(question, 4)
    result = chain.invoke({"results": results, "question": question})
    print(result)

# Prompt template:

# You are a helpful assistant. Use the following context in your response: {results}
# Answer the user's question using ONLY the context above where relevant, show the sources also; if no answer is available, say you don't know."
# Here is the question to answer: {question}

#Answer the user's question using ONLY the context above, if you cannot answer based on the context, say you don't know."