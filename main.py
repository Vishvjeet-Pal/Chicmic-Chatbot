import os
from fastapi import FastAPI, Body
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_groq import ChatGroq
from config import settings
from seed.holidays import HOLIDAYS
# from ingest.holiday_ingest import ingest_holidays_from_api
from seed.timesheets import timesheets

app = FastAPI()

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
"""

agent = None   # global

@app.on_event("startup")
async def startup():
    global agent

    # ingest_holidays_from_api()
    client = MultiServerMCPClient({
        "db_server": {
            "transport": "stdio",
            "command": "python",
            "args": [server_path]
        }
    })

    tools = await client.get_tools()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

@app.post("/ask")
async def ask_chatbot(query: str, authorization: str, request_data: dict=Body(default={})):
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config={
            "configurable":{
                "auth_token": authorization,
                "request_data": request_data,
                "query": query
            }
        }
    )
    return {"answer": result["messages"][-1].content}
 
@app.get("/holidays")
async def get_holiday_calendar():
    return HOLIDAYS

@app.get("/timesheets")
def get_timesheets():
    return timesheets