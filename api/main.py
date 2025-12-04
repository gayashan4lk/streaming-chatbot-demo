import os
import asyncio
from dotenv import load_dotenv
from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model_name="gpt-4o-mini-2024-07-18",
    openai_api_key=OPENAI_API_KEY,
    streaming=True
)

async def generate_response(message: str):
    for chunk in llm.stream([HumanMessage(content=message)]):
        print(chunk)
        # yield f"data: {chunk.content} \n\n"
        yield f"{chunk.content}"
        await asyncio.sleep(0.01)

# Testing event streaming (SSE) with frontend
async def event_generator(data: str):
    for i in range(10):
        await asyncio.sleep(0.1)
        print (f"data: Hi Processed chunk {i + 1} of input: {data}\n\n")
        yield f"data: Hi Processed chunk {i + 1} of input: {data} \n\n"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message","")
    return StreamingResponse(generate_response(message), media_type="text/event-stream")

# Testing event streaming (SSE) with frontend
@app.get("/stream")
async def stream(input: str = "default"):
    return StreamingResponse(event_generator(input), media_type="text/event-stream")
