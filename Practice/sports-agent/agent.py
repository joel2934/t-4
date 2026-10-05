import operator

from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langchain_openrouter import ChatOpenRouter

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools import get_cricket_scores


# ==================================================
# 1. LLM - OPENROUTER
# ==================================================

llm = ChatOpenRouter(
    model="openrouter/free",
    temperature=0
)


# ==================================================
# 2. SPORTS TOOLS
# ==================================================

sports_tools = [
    get_cricket_scores
]


# Give the LLM access to the sports tool
sports_llm = llm.bind_tools(
    sports_tools
)


# ==================================================
# 3. STATE
# ==================================================

class SportsState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        operator.add
    ]


# ==================================================
# 4. SPORTS AGENT
# ==================================================

def sports_agent(
    state: SportsState
):

    print("\n[SPORTS AGENT] Thinking...")


    response = sports_llm.invoke(
        state["messages"]
    )


    # Check whether the LLM requested a tool
    tool_calls = getattr(
        response,
        "tool_calls",
        None
    )


    if tool_calls:

        print(
            "[SPORTS AGENT] Tool call requested:"
        )

        for call in tool_calls:

            print(
                f"  → {call['name']}"
            )

    else:

        print(
            "[SPORTS AGENT] "
            "Final answer generated."
        )


    return {
        "messages": [
            response
        ]
    }


# ==================================================
# 5. ROUTER
# ==================================================

def route_sports_agent(
    state: SportsState
):

    last_message = (
        state["messages"][-1]
    )


    tool_calls = getattr(
        last_message,
        "tool_calls",
        None
    )


    if tool_calls:

        print(
            "[ROUTER] "
            "Tool call detected → tools"
        )

        return "tools"


    print(
        "[ROUTER] "
        "No tool call → END"
    )

    return END


# ==================================================
# 6. CREATE GRAPH
# ==================================================

sports_graph = StateGraph(
    SportsState
)


# ==================================================
# 7. ADD SPORTS AGENT NODE
# ==================================================

sports_graph.add_node(
    "sports_agent",
    sports_agent
)


# ==================================================
# 8. ADD TOOL NODE
# ==================================================

sports_graph.add_node(
    "tools",
    ToolNode(sports_tools)
)


# ==================================================
# 9. START
# ==================================================

sports_graph.set_entry_point(
    "sports_agent"
)


# ==================================================
# 10. CONDITIONAL ROUTING
# ==================================================

sports_graph.add_conditional_edges(

    "sports_agent",

    route_sports_agent,

    {
        "tools": "tools",
        END: END
    }
)


# ==================================================
# 11. TOOL → SPORTS AGENT
# ==================================================

sports_graph.add_edge(
    "tools",
    "sports_agent"
)


# ==================================================
# 12. COMPILE
# ==================================================

sports_app = sports_graph.compile()