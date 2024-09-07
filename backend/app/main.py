from typing import Annotated, Literal, TypedDict
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langserve import add_routes
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper

from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from langgraph.graph import StateGraph, END, START

from collections import OrderedDict
import os
load_dotenv()


class RequestModel(BaseModel):
    message: str
    session_id:str
    llm: str
    model_name : str

groq_api_key = os.getenv("GROQ_API_KEY") 
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = os.getenv("LANGCHAIN_PROJECT")



#groq_api_key = st.secrets["GROQ_API_KEY"]
#os.environ['LANGCHAIN_API_KEY'] = st.secrets["LANGCHAIN_API_KEY"]
#os.environ['LANGCHAIN_PROJECT'] = st.secrets["LANGCHAIN_PROJECT"]

os.environ['LANGCHAIN_TRACING_V2'] = "true"

model = ChatGroq(model="gemma-7b-it")


parser = StrOutputParser()

## inmemory chat history
store = OrderedDict()

def get_session_history(session_id):
    ## Handle max 5 sessions
    if len(store) > 4 :
        store.popitem(last=False)
    
    if session_id not in store :
        store[session_id]= []
    return store[session_id]

with_message_history = RunnableWithMessageHistory(model,get_session_history)

chain = with_message_history|parser

## DataClass

class DecisionRouter(BaseModel):
    decision : Literal['RAG', 'General'] = Field(..., description="Chose correct option based on user input, If User ask about Tanweer , Use RAG else General")



## Vector DB Init
embedding = OpenAIEmbeddings()
db_path = os.path.join(os.path.dirname(__file__), "faiss_index")
db = FAISS.load_local(db_path, embedding ,allow_dangerous_deserialization=True)

vector_store_wrapper = VectorStoreIndexWrapper(vectorstore= db)

##  LLMs
router_llm_structured,general_llm = None,None

def get_llm(llm_name, model):
    if llm_name == "GROQ":
        #'llama-3.1-8b-instant'
        router_llm = ChatGroq(model=model)

        router_llm_structured = router_llm.with_structured_output(DecisionRouter)

        general_llm = ChatGroq(model=model)

    elif llm_name == "OPENAI":
        #gpt-4o-mini
        router_llm = ChatOpenAI(model=model)

        router_llm_structured = router_llm.with_structured_output(DecisionRouter)

        general_llm = ChatOpenAI(model=model)
    else:
        router_llm = ChatGroq(model='llama-3.1-8b-instant')

        router_llm_structured = router_llm.with_structured_output(DecisionRouter)

        general_llm = ChatGroq(model='llama-3.1-8b-instant')

    
    return router_llm_structured, general_llm








## State

from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


## Node Agents

def input_router(state: AgentState):
    decision = router_llm_structured.invoke(state['messages'])

    return decision.decision



def general_llm_agent(state : AgentState):

    return {'messages' : [general_llm.invoke(state['messages'])] }


def rag_query(state : AgentState):
    print(state)
    response = vector_store_wrapper.query(state['messages'][-1].content, general_llm)

    return {'messages' :[response] }

## Graph Builder

from langgraph.graph import StateGraph, END, START

workflow = StateGraph(AgentState)

workflow.add_node('General' ,general_llm_agent)
workflow.add_node('RAG', rag_query)

workflow.add_conditional_edges(START,input_router )
workflow.add_edge('General', END)
workflow.add_edge('RAG', END)

graph = workflow.compile()

## App defination

origins = [
    "https://tangpt.tanflix.me/",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]



app = FastAPI(root_path="/api", title="TanGPT API", version="1", description="TanGPT API Server using langchain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/invoke")
async def get_response(request : RequestModel):

    
    config = {"configurable": {"session_id": request.session_id}}
    return chain.invoke([HumanMessage(request.message)], config=config)

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

@app.post("/chat")
async def get_response(request: RequestModel):
    try:
        global router_llm_structured, general_llm
        router_llm_structured, general_llm = get_llm(request.llm, request.model_name)
        
        conversation_history = get_session_history(request.session_id)
        conversation_history.append(("user", request.message))
        
        result = graph.invoke({'messages': conversation_history})
        
        assistant_response = result['messages'][-1].content
        
        conversation_history.append(("assistant", assistant_response))
        
        return JSONResponse(
            content={"response": assistant_response},
            status_code=status.HTTP_200_OK
        )
    
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(ve)}"
        )
    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Missing key in response: {str(ke)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


    


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app,host="localhost", port=8080)
