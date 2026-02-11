import os
from fastapi import FastAPI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

app = FastAPI()

llm = ChatOllama(model="llama3.1", temperature=0)

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



system_prompt = """You are a Task Management Assistant. Use tools to query the DB. Answer user queries based on the retrieved information. If you don't know the answer, say you don't know. ONLY answer what is asked. DO NOT provide extra information. If you are not sure which tool to use, use login_credential tool first to check if the answer is in the FAQs.
If you can not decide which tool to use, say you don't know
After receiving tool results, you MUST return the final answer to the user.
Do NOT call tools again if the answer is found.
Do NOT output JSON.
Return ONLY the final answer text.
DO NOT mention the tools in your answer.
"""


@app.post("/ask")
async def ask_chatbot(query: str):
    tools = await get_mcp_tools()
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return {"answer": result["messages"][-1].content}
    # result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
    # answer = extract_answer(result)
    # return {"answer": answer}
#     result = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

#     answer = next(
#     (
#         m.artifact["structured_content"]["result"]
#         for m in reversed(result["messages"])
#         if getattr(m, "artifact", None)
#         and "structured_content" in m.artifact
#         and "result" in m.artifact["structured_content"]
#     ),
#     "No answer found"
# )

#     return {"answer": answer}

