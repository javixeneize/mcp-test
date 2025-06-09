import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model
model = init_chat_model("openai:gpt-4.1")

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["math_server.py"],  # make sure you set the correct path
            "transport": "stdio",
        },
        # "weather": {
        #     # make sure you start your weather server on port 8000
        #     "url": "http://localhost:8000/mcp",
        #     "transport": "streamable_http",
        # },
        "github": {
            "transport": "stdio",
            "command": "docker",
            "args": [
                "run", "-i", "--rm",
                "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server"
            ],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": XXXX
  }
        }
    }
)

tools = asyncio.run(client.get_tools())

def call_model(state: MessagesState):
    response = model.bind_tools(tools).invoke(state["messages"])
    return {"messages": response}


async def main():
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_node(ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")
    graph = builder.compile()
    # math_response = await graph.ainvoke({"messages": "what's (3 + 5) x 12?"})
    # weather_response = await graph.ainvoke({"messages": "what is the weather in nyc?"})
    # print (math_response)
    # print (weather_response)
    gh_response = await graph.ainvoke({"messages": "Create an empty file called test.md in the repository javixeneize/mcp-javi-v2 in the branch main. If the branch does not exist, create it too. Then, calculate 40*2"})
    # gh_response = await graph.ainvoke({"messages": "Calculate 3+5"})
    print (gh_response.get('messages')[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
