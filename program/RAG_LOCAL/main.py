# main.py

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3.2")
# 2. Answer the user’s question using only the information in the relevant context.
template = """
You are a highly helpful, precise assistant. Use the following context and only this context to answer the user’s question:
{reviews}

Instructions:
1. First, identify the parts of the context that are most relevant to answering the question.
2. Answer the user’s question using only the information in the relevant context.
3. If the context does not contain the answer, respond: “I don’t know based on the provided context.”
4. Provide answers that are concise, complete, and well-structured in a free flowing text.
5. Avoid adding any assumptions, opinions, or information not present in the context.
6. Be polite, professional, and helpful.
7. Do not cite sources.

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

    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)

# Prompt template:

# You are a helpful assistant. Use the following context in your response: {reviews}
# Answer the user's question using ONLY the context above where relevant, show the sources also; if no answer is available, say you don't know."
# Here is the question to answer: {question}