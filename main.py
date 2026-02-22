import os
from fastapi import FastAPI, Body, Header
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessageChunk
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from functools import wraps
from fastapi.responses import FileResponse, StreamingResponse
import json
from langchain_groq import ChatGroq
from config import settings
from seed.holidays import HOLIDAYS
# from ingest.holiday_ingest import ingest_holidays_from_api
from seed.timesheets import timesheets

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# llm = ChatOllama(model="llama3.1", temperature=1,base_url="http://192.180.5.31:11434")
# llm = ChatOllama(model="qwen2.5:7b", temperature=0,base_url="http://192.180.5.31:11434")
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0, api_key=settings.GROQ_API_KEY)

current_dir = os.path.dirname(os.path.abspath(__file__))
server_path = os.path.join(current_dir, "mcp_server.py")

async def get_mcp_tools():
    client = MultiServerMCPClient({
        "db_server": {
            "transport": "stdio",
            "command": "python", 
            "args": [server_path]
        }
    })
    return await client.get_tools()



system_prompt = """You are a Chatbot Assistant of "Chicmic Studios" company. Use tools to query the DB. Answer user queries based on the retrieved information. If you don't know the answer, say you don't know. ONLY answer what is asked. DO NOT provide extra information. If you are not sure which tool to use, use search_pdf_policy tool first to check if the answer is in the FAQs.
IMPORTANT INSTRUCTION: 
- IF YOU CAN NOT DECIDE WHICH TOOL TO USE, SAY "I don't know".
- NEVER return internal json data to user. 
- If date is mentioned but year is not mentioned in user's query, DO NOT ASSUME year. Just provide date without year.
After receiving tool results, you MUST return the final answer to the user.
Do NOT call tools again if the answer is found.
Return ONLY the final answer text.
DO NOT mention the tools used.
STRICT RULES:
    - IF NO YEAR IS MENTIONED IN DATE, DO NOT ASSUME THE YEAR.
If the user asks ANYTHING related to holidays
   (examples: next holiday, upcoming holidays, holiday list, holiday date, company holidays, leave with holiday, etc.)
   → ALWAYS return the COMPLETE Holiday Calendar provided in the context for user reference.
     Only mention the holidays which are present in the Holiday Calendar document provided in the context. Do NOT generate or assume any holiday information that is not in the document.
NOTE: Use get_user_profile_data tool if user asks about LEAVE BALANCE or PROFILE DATA. Provide complete profile data if user asks about its profile data.
"""

agent = None   # global

def wrap_with_auth(tool: BaseTool):
    """Middleware to inject auth_token and request_data into the tool execution."""
    original_arun = tool._arun 

    @wraps(original_arun)
    async def wrapped_arun(*args, **kwargs):
        config = kwargs.get("config")
        if config and "configurable" in config:
            # 1. Extract values from config
            token = config["configurable"].get("auth_token")
            req_data = config["configurable"].get("request_data")

            # 2. Inject into kwargs if the tool expects them
            # We check tool.args to see if the tool actually expects these parameters
            # This prevents "Unexpected Argument" errors for tools that don't need them
            if "auth_token" in tool.args or "auth_token" in kwargs:
                kwargs["auth_token"] = token
            
            if "request_data" in tool.args:
                kwargs["request_data"] = req_data

        return await original_arun(*args, **kwargs)

    object.__setattr__(tool, "_arun", wrapped_arun)
    return tool

@app.on_event("startup")
async def startup():
    global agent
    client = MultiServerMCPClient({
        "db_server": {
            "transport": "stdio",
            "command": "python",
            "args": [server_path]
        }
    })

    raw_tools = await client.get_tools()
    
    authenticated_tools = [wrap_with_auth(t) for t in raw_tools]

    agent = create_agent(
        model=llm,
        tools=authenticated_tools,
        system_prompt=system_prompt,
    )

@app.get("/")
def serve_index():
    return FileResponse("index.html")

@app.post("/ask")
async def ask_chatbot(query: str, Authorization:str=Header(...), request_data: dict=Body(None)):
    # return request.headers
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config={
            "configurable":{
                "auth_token": Authorization,
                "request_data": request_data or dict()
            }
        }
    )
    return {"answer": result}#["messages"][-1].content}
 

from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

@app.post("/ask-stream")
async def ask_chatbot_stream(
    query: str,
    Authorization: str = Header(...),
    request_data: dict = Body(None)
):
    if agent is None:
        return {"error": "Agent not initialized"}

    async def event_generator():
        try:
            async for msg, metadata in agent.astream(
                {"messages": [HumanMessage(content=query)]},
                config={
                    "configurable": {
                        "auth_token": Authorization,
                        "request_data": request_data or {}
                    }
                },
                stream_mode="messages", # Note: LangGraph returns (msg, metadata)
            ):
                # We only want chunks from the final 'agent' or 'model' node
                # to avoid streaming internal tool logs.
                if isinstance(msg, AIMessageChunk):
                    content = msg.content
                    if content:
                        yield str(content)
                        
        except Exception as e:
            yield f" [ERROR]: {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream", # Changed to event-stream for better browser support
        headers={
            "X-Accel-Buffering": "no",  # Disables buffering in Nginx
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/streaming")
def serve_index_streaming():
    return FileResponse("index_streaming.html")

@app.get("/holidays")
async def get_holiday_calendar():
    return HOLIDAYS

@app.get("/timesheets")
def get_timesheets():
    return timesheets