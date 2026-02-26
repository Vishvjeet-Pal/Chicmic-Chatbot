import os
from fastapi import FastAPI, Body, Header
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessageChunk, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from functools import wraps
from fastapi.responses import FileResponse, StreamingResponse
from langchain_groq import ChatGroq
from config import settings
from seed.holidays import HOLIDAYS
import asyncio
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
# llm = ChatOllama(model="gpt-oss:20b", temperature=1,base_url="http://192.180.5.31:11434", streaming=True)
# llm = ChatOllama(model="llama3.1", temperature=0,base_url="http://192.180.5.31:11434")
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=settings.GROQ_API_KEY, streaming=True)

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



system_prompt = """You are a Chatbot Assistant of "Chicmic Studios" company. Use tools to query the DB. Answer user queries based on the retrieved information. If you don't know the answer, say you don't know. ONLY answer what is asked. DO NOT provide extra information.
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
    - IF ONLY MONTH IS MENTIONED IN DATE, DO NOT TAKE ANY VALUE FOR DATE ARGUMENT
If user asks about leave deduction use get_daily_attendence tool.
If the user asks ANYTHING related to holidays
   (examples: next holiday, upcoming holidays, holiday list, holiday date, company holidays, leave with holiday, etc.)
   → ALWAYS call list_holidays tool and return the COMPLETE Holiday Calendar for user reference.
     Only mention the holidays which are present in the Holiday Calendar document provided in the context. Do NOT generate or assume any holiday information that is not in the document.
NOTE: 
Use get_user_profile_data tool if user asks about LEAVE BALANCE or PROFILE DATA and get_user_leaves if user asks about PENDING/APPROVED LEAVES. Treat leave balance and pending leave differently. Provide complete profile data if user asks about its profile data.
Use my_timesheet_search tool when user asks about timesheet details
Use get_daily_attendance tool when user asks about ATTENDANCE, ABSENT/PRESENT STATUS, leave deduction
Use get_user_leaves if user asks about its own leaves and leave_application tool if user asks about other employees leaves.
If user asks about leave details of employees by specifying employee name, team, employee id, reporting manager, leave type, reason, date or status, use leave_application tool to get the details. If no employee name, team, employee id, reporting manager, leave type, reason, date or status is specified in user's query, then use get_user_leaves tool to get the leave details of the user itself.
If user asks about late come requests of employees by specifying employee name, team, employee id, reporting manager then use late_arrival_requests tool. If no employee name, team, employee id, reporting manager is specified, then use my_late_come_requests tool to provide late come details of the user itsel.
If user asks about timesheet of employees by specifying employee name, team, employee id, use timesheet_summary tool. If no employee name, team, employee id is mentioned use my_timesheet_search tool to provide timesheet details of the user itself.
If user asks about manual hour request of employees by specifying employee name, employee id, use manual_hours_requests_other tool. If no employee name, employee id is mentioned use manual_hour_requests tool to provide manual hours requests of the user itself.
If user asks about it assets assigned to employees by specifying employee name, employee id, use asset_list tool. If no employee name, employee id, is provided use user assets tool for providing asset details of the current user itself.
If user asks about screening request details of candidates being/applied for interview use screening_request tool.
"""

agent = None   

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
    return {"answer": result["messages"][-1].content}


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
                config={"configurable": {"auth_token": Authorization, "request_data": request_data or {}}},
                stream_mode="messages",
            ):
                
                # yield(str(msg))
                # Detect tool calls
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    yield f"\n[Status: Searching {msg.tool_calls[0]['name']}...]\n"
                
                # Yield content chunks
                elif (isinstance(msg,AIMessage) or isinstance(msg,AIMessageChunk)) and hasattr(msg, "content") and msg.content:
                    if isinstance(msg.content, str):
                        yield msg.content
                    elif isinstance(msg.content, list):
                        for part in msg.content:
                            if isinstance(part, dict) and "text" in part:
                                yield part["text"]

        except asyncio.CancelledError:
            # This is triggered when the user clicks 'Stop' (AbortController)
            print(f"Client disconnected. Stopping LLM for query: {query}")
            # The LLM execution will stop here because the generator is broken
            raise 
        except Exception as e:
            yield f" [ERROR]: {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",
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