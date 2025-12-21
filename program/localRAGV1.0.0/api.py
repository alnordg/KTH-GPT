# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model and Prompts
model = OllamaLLM(model="llama3.2")

template = """
You are a highly helpful, precise assistant. Use the following context and only this context to answer the user’s question:
{reviews}

Instructions:
1. First, identify the parts of the context that are most relevant to answering the question.
2. Answer the user’s question using only the information in the relevant context.
3. If the context does not contain the answer, respond: “I don’t know based on the provided context.”
4. Provide answers that are concise, complete, and well-structured.
5. Avoid adding any assumptions, opinions, or information not present in the context.
6. Be polite, professional, and helpful.

User’s question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        question = request.question
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Retrieve context
        reviews = retriever.invoke(question)
        
        # Invoke chain
        result = chain.invoke({"reviews": reviews, "question": question})
        
        return AnswerResponse(answer=result)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
