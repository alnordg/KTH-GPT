from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from embeddings import retriever

model = OllamaLLM(model="llama3.2")
# 2. Answer the user’s question using only the information in the relevant context.

template = """
You are a highly helpful, precise assistant. Use the following context and only this context to answer the user’s question:
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

    results = retriever.invoke(question)
    result = chain.invoke({"results": results, "question": question})
    print(result)

# Prompt template:

# You are a helpful assistant. Use the following context in your response: {results}
# Answer the user's question using ONLY the context above where relevant, show the sources also; if no answer is available, say you don't know."
# Here is the question to answer: {question}