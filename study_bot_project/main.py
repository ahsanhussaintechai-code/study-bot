from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from database import save_chat, get_chat_history

load_dotenv()

app = FastAPI()

# LLM Setup
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="mixtral-8x7b-32768")

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.get("/")
def home():
    return {"message": "Study Bot API is Live!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 1. Retrieve Context (Memory)
    past_chats = await get_chat_history(request.user_id)
    context = ""
    for chat in past_chats:
        context += f"User: {chat['user_message']}\nBot: {chat['bot_response']}\n"

    # 2. System Prompt
    system_prompt = SystemMessage(content="You are a helpful Study Bot. Answer academic questions clearly and concisely.")
    
    # 3. Combine context and new message
    full_prompt = f"Previous Conversation:\n{context}\nNew Question: {request.message}"
    user_message = HumanMessage(content=full_prompt)

    # 4. Get Response from LLM
    response = llm.invoke([system_prompt, user_message])
    bot_text = response.content

    # 5. Save to MongoDB
    await save_chat(request.user_id, request.message, bot_text)

    return {"response": bot_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)