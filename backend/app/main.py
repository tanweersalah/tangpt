from fastapi import FastAPI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

load_dotenv()


class RequestModel(BaseModel):
    message: str

groq_api_key = os.getenv("GROQ_API_KEY") 
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = os.getenv("LANGCHAIN_PROJECT")



#groq_api_key = st.secrets["GROQ_API_KEY"]
#os.environ['LANGCHAIN_API_KEY'] = st.secrets["LANGCHAIN_API_KEY"]
#os.environ['LANGCHAIN_PROJECT'] = st.secrets["LANGCHAIN_PROJECT"]

os.environ['LANGCHAIN_TRACING_V2'] = "true"

model = ChatGroq(model="llama3-70b-8192")


parser = StrOutputParser()

store = {}

def get_session_history(session_id):
    if session_id not in store :
        store[session_id]= ChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(model,get_session_history)

chain = with_message_history|parser

## App defination

app = FastAPI(root_path="/api", title="TanGPT API", version="1", description="TanGPT API Server using langchain")

config = {"configurable": {"session_id": "chat1"}}

@app.post("/invoke")
async def get_response(request : RequestModel):
    return chain.invoke([HumanMessage(request.message)], config=config)
    


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app,host="localhost", port=8080)
