from typing import Annotated, Literal
from typing_extensions import TypedDict
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langserve import add_routes
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from youtube_api import YouTubeAPI
from langgraph.prebuilt import ToolNode,tools_condition
from langchain.chains.summarize import load_summarize_chain
from langgraph.graph import StateGraph, END, START
from langchain_text_splitters import RecursiveCharacterTextSplitter



from collections import OrderedDict
import os

# init env keys
load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = "true"

yt_api = YouTubeAPI()



## DataClass


## State

from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    is_authenticated: bool
    auth_required: bool
    llm: str
    url_to_summarize : str
    next_node : str


class DecisionRouter(BaseModel):
    decision : Literal['RAG', 'General', 'Media', 'SummarizeVideo'] = Field(..., description="Chose correct option based on user input, 1. If User ask any information related to Tanweer use RAG  ,2. If user needs a video or youtube links use Media,3. If user asking for summarizing a video use SummarizeVideo, else General")
    link: str = Field(..., description="link for the video if user asking for summarizing any video , else keep it blank ")
class SessionStore(BaseModel):
    chat_history :list
    state: AgentState
class RequestModel(BaseModel):
    message: str
    session_id:str
    llm: str
    model_name : str

## utils
def document_splitter(document , chunk_size = 1000, chunk_overlap = 200):
    splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
    return splitter.split_documents(document)


## inmemory session history
store = OrderedDict()

def get_session_history(session_id) -> AgentState:
    ## Handle max 5 sessions
    if len(store) > 4 :
        store.popitem(last=False)
    
    if session_id not in store :
        #store[session_id]= SessionStore(chat_history=[],  state={})
        store[session_id]= AgentState(messages=[], is_authenticated=False, auth_required=False)

    return store[session_id]


def update_session_history(session_id, chat_history, auth_required , state):
    store[session_id].chat_history = chat_history
    store[session_id].auth_required = auth_required
    store[session_id].state = state




## Vector DB Init
embedding = OpenAIEmbeddings()
db_path = os.path.join(os.path.dirname(__file__), "faiss_index")
db = FAISS.load_local(db_path, embedding ,allow_dangerous_deserialization=True)

vector_store_wrapper = VectorStoreIndexWrapper(vectorstore= db)

##  LLMs
router_llm_structured,general_llm = None,None

openai_llm = ChatOpenAI()

def get_llm(llm_name, model, router_llm_openai=False):
    if llm_name == "GROQ":
        #'llama-3.1-8b-instant'
        router_llm = ChatGroq(model=model)

        general_llm = ChatGroq(model=model)

    elif llm_name == "OPENAI":
        #gpt-4o-mini
        router_llm = ChatOpenAI(model=model)

        general_llm = ChatOpenAI(model=model)
    else:
        router_llm = ChatGroq(model='llama-3.1-8b-instant')

        general_llm = ChatGroq(model='llama-3.1-8b-instant')

    if router_llm_openai:
        router_llm = ChatOpenAI()
    router_llm_structured = router_llm.with_structured_output(DecisionRouter)

   
    
    return router_llm_structured, general_llm

## Tools

@tool
def get_media(search_text):
    """Returns the video link and video title for given search_text, select the most relevant one"""

    global yt_api
    response = yt_api.search( search_text, max_results=1, video_type="video")
    return response

tools = [get_media]




## Node Agents

auth_message = """
🔐 Oops! Authentication needed for OpenAI LLMs! 🤖 \n
Please enter the secret code 🗝️ or switch to a different LLM to proceed. 🔄
"""

def input_router(state: AgentState):
    
    if state.get('auth_required', False) :
        return {'next_node' : 'END', 'url_to_summarize': ""}
    
    decision = router_llm_structured.invoke(state['messages'])
    

    return {'next_node' : decision.decision, 'url_to_summarize': decision.link}

def auth(state: AgentState):
    
    auth_required = False
    # Check previos state
    is_authenticated = state.get('is_authenticated', False)
    messages = []

    if state['llm'] == 'OPENAI':
        

        if state.get('auth_required', False):
            pw = state['messages'].pop()
            if os.environ.get('SUPERSECRET') == pw.content:
                is_authenticated = True
                

        if not is_authenticated:
            auth_required = True
            is_authenticated = False
            messages = [("ai", auth_message)]
        

    return { 'is_authenticated' : is_authenticated,
                 'auth_required' : auth_required, 'messages' : messages}
    
    

def general_llm_agent(state : AgentState):

    return {'messages' : [general_llm.invoke(state['messages'])] }


def rag_query(state : AgentState):
    
    response = vector_store_wrapper.query(state['messages'][-1].content, general_llm)

    return {'messages' :[response] }

def media_query(state: AgentState):
    
    model_with_yt = openai_llm.bind_tools(tools)
    
    response = model_with_yt.invoke(state['messages'])

    return {'messages' :[response], 'video' : True }

def summarize_content(state: AgentState):
    print('doc',state)
    youtube_doc=yt_api.summarize_content(state['url_to_summarize'])
    
    docs = document_splitter(youtube_doc)[:10]

    chain = load_summarize_chain(llm=general_llm, chain_type='refine')

    response = chain.invoke(docs)

    return {'messages' :[response['output_text']] }

## Graph Builder

from langgraph.graph import StateGraph, END, START

workflow = StateGraph(AgentState)

workflow.add_node('Auth', auth)
workflow.add_node('Router' ,input_router)

workflow.add_node('General' ,general_llm_agent)
workflow.add_node('RAG', rag_query)
workflow.add_node('Media', media_query)
workflow.add_node('Summarize', summarize_content)

tool_node = ToolNode(tools=tools)
workflow.add_node('tools', tool_node)

workflow.add_edge( 'tools','Media')
workflow.add_edge(START,'Auth' )
workflow.add_edge('Auth', 'Router' )
workflow.add_conditional_edges('Router',lambda x : x['next_node'] ,{
    "END" : END,
    'General' : 'General',
    'RAG' : 'RAG',
    'SummarizeVideo' : 'Summarize',
    'Media' : 'Media'
})
workflow.add_conditional_edges('Media',tools_condition )
workflow.add_edge('General', END)
workflow.add_edge('RAG', END)
workflow.add_edge('Summarize', END)

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
        router_llm_structured, general_llm = get_llm(request.llm, request.model_name, True)
        
        session = get_session_history(request.session_id)
        

        
        session.get('messages').append(("user", request.message))
        session['llm'] = request.llm

        
        result = graph.invoke(session)

        assistant_response = result['messages'][-1].content
        
        session['auth_required'] = result.get('auth_required', False)
        session['is_authenticated'] = result.get('is_authenticated', False)

        if session.get('auth_required'):
            
            return JSONResponse(
            content={"response": assistant_response, "auth_required" : True},
            status_code=status.HTTP_200_OK
        )

        session.get('messages').append(("assistant", assistant_response))
        
        
        return JSONResponse(
            content={"response": assistant_response, "auth_required" : False},
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
