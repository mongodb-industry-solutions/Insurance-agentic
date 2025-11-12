
import functools
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.prebuilt import ToolNode
from agent_definition import chatbot_agent
from agent_tools import tools

import logging

from bson import ObjectId

def serialize_object(obj):
    """Recursively serialize ObjectId in a dictionary or list."""
    if isinstance(obj, dict):
        return {key: serialize_object(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_object(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    try: 
        result = agent.invoke(state)
    
        # Serialize the result to handle ObjectId
        result = serialize_object(result)
        
        # Convert the agent output into a format suitable for the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        
        return {
            "messages": [result],
            "sender": name,
        }
    except TypeError as e:
        # Log a warning and continue
        logging.warning(f"Serialization warning: {e}. Skipping problematic data.")
        return {
            "messages": [],
            "sender": name,
        }


chatbot_node = functools.partial(agent_node, agent=chatbot_agent, name="Claim adjuster helper")
tool_node = ToolNode(tools, name="tools")