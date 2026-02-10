# main.py
from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from mcp_server import mcp

app = FastAPI()

# 1. Setup Local LLM (Ollama)
# Note: Ensure Ollama is running on your machine (default port 11434)
llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    format="json"  # Forces structured output which helps with tool calling
)

# 2. Extract Tools from MCP Server
tools = mcp.get_tools()

# 3. Define the Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a local University Assistant. Use your database tools to help students."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 4. Initialize the Agent
# Llama 3.1+ works best with the 'tool_calling_agent'
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/ask")
async def ask_chatbot(query: str):
    # Process query through the local agent
    response = await agent_executor.ainvoke({"input": query, "chat_history": []})
    return {"answer": response["output"]}