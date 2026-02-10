# # main.py
from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from mcp_server import mcp, search_faq, get_policy_by_category

app = FastAPI()

# 1. Setup Local LLM (Ollama)
# Note: Ensure Ollama is running on your machine (default port 11434)
llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    format="json"  # Forces structured output which helps with tool calling
)

# 2. Extract Tools from MCP Server
# tools = mcp.get_tools()
tools = [search_faq, get_policy_by_category]  # Directly using the tool functions for simplicity

# 3. Define the Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a local University Assistant. Use your database tools to help students."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    
])

# 4. Initialize the Agent
# Llama 3.1+ works best with the 'tool_calling_agent'
agent = create_agent(llm, tools, system_prompt=prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/ask")
async def ask_chatbot(query: str):
    # Process query through the local agent
    response = await agent.ainvoke({"input": query, "chat_history": []})
    return {"answer": response["output"]}


# from fastapi import FastAPI
# from langchain_ollama import ChatOllama
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from mcp_server import mcp

# app = FastAPI()

# # Setup LLM
# llm = ChatOllama(
#     model="llama3.1",
#     temperature=0,
# )

# agent_executor = None   # will initialize on startup


# @app.on_event("startup")
# async def startup_event():
#     global agent_executor

#     # 1. Get MCP tools (async)
#     tools = await mcp.get_tools()

#     # 2. Prompt
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "You are a local University Assistant. Use your database tools to help students."),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("human", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ])

#     # 3. Create Tool Calling Agent
#     agent = create_tool_calling_agent(llm, tools, prompt)

#     # 4. Executor
#     agent_executor = AgentExecutor(
#         agent=agent,
#         tools=tools,
#         verbose=True,
#     )


# @app.post("/ask")
# async def ask_chatbot(query: str):
#     response = await agent_executor.ainvoke({
#         "input": query,
#         "chat_history": []
#     })
#     return {"answer": response["output"]}
