import os
from fastapi import FastAPI, Body, Header, Request
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from functools import wraps
from fastapi.responses import FileResponse

# from langchain_groq import ChatGroq
from config import settings
from seed.holidays import HOLIDAYS
# from ingest.holiday_ingest import ingest_holidays_from_api
from seed.timesheets import timesheets

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
llm = ChatOllama(model="llama3.1", temperature=0)
# llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=settings.GROQ_API_KEY)

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
If you can not decide which tool to use, say you don't know
After receiving tool results, you MUST return the final answer to the user.
Do NOT call tools again if the answer is found.
Return ONLY the final answer text.
DO NOT mention the tools used.
If the user asks ANYTHING related to holidays
   (examples: next holiday, upcoming holidays, holiday list, holiday date, company holidays, leave with holiday, etc.)
   → ALWAYS return the COMPLETE Holiday Calendar provided in the context for user reference.
     Only mention the holidays which are present in the Holiday Calendar document provided in the context. Do NOT generate or assume any holiday information that is not in the document.
NOTE: Use get_user_profile_data tool if user asks about LEAVE BALANCE or PROFILE DATA. Provide complete profile data if user asks about its profile data.
When the user mentions a date, extract it in ISO format (YYYY-MM-DD).

If no date is mentioned, return today's date.
Return output strictly in this JSON format:

{
  "date": "YYYY-MM-DD"
}
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
        system_prompt=system_prompt
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
 
@app.get("/holidays")
async def get_holiday_calendar():
    return HOLIDAYS

@app.get("/timesheets")
def get_timesheets():
    return timesheets