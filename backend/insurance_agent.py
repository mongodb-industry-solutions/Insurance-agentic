import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict
from bson import ObjectId
import json

from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition

from agent_node_definition import chatbot_node, tool_node

import pprint
from typing import Dict, List

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

def serialize_object(obj):
    """Recursively serialize ObjectId in a dictionary or list."""
    if isinstance(obj, dict):
        return {key: serialize_object(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_object(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

def insurance_agent(image_description: str) -> List[BaseMessage]:
    # State Definition
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    # Agentic Workflow Definition
    workflow = StateGraph(AgentState)

    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("chatbot")
    workflow.add_conditional_edges("chatbot", tools_condition, {
                                "tools": "tools", END: END})

    workflow.add_edge("tools", "chatbot")

    def process_event(event: Dict) -> List[BaseMessage]:
        new_messages = []
        for value in event.values():
            if isinstance(value, dict) and "messages" in value:
                for msg in value["messages"]:
                    if isinstance(msg, BaseMessage):
                        new_messages.append(msg)
                    elif isinstance(msg, dict) and "content" in msg:
                        # Serialize ObjectId in additional_kwargs
                        additional_kwargs = serialize_object(msg.get("additional_kwargs", {}))
                        new_messages.append(
                            AIMessage(
                                content=msg["content"],
                                additional_kwargs=additional_kwargs,
                            )
                        )
                    elif isinstance(msg, str):
                        new_messages.append(ToolMessage(content=msg))
        return new_messages

    # Graph Compilation and visualization
    graph = workflow.compile()
    # Process and View Response
    object_ids = []  # Collect ObjectIds here
    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    content="This is the description of the accident: " + str(image_description),
                )
            ]
        },
        {"recursion_limit": 15},
    )

    new_messages = []  # Initialize new_messages to collect processed messages

    for event in events:
        try:
            # Serialize the event to handle ObjectId
            serialized_event = serialize_object(event)
            
            print("Event:")
            pprint.pprint(serialized_event)
            print("---")

            # Process the event and extract messages
            processed_messages = process_event(serialized_event)
            new_messages.extend(processed_messages)

            # Extract ObjectId from ToolMessage content if present
            if "tools" in serialized_event and "messages" in serialized_event["tools"]:
                for tool_message in serialized_event["tools"]["messages"]:
                    if isinstance(tool_message, ToolMessage):
                        try:
                            # Parse the content as JSON to extract the ObjectId
                            tool_content = json.loads(tool_message.content)
                            if "object_id" in tool_content:
                                object_ids.append(tool_content["object_id"])
                        except json.JSONDecodeError:
                            print("Failed to parse ToolMessage content as JSON.")

        except TypeError as e:
            # Log a warning and continue
            print(f"Serialization warning: {e}. Skipping problematic event.")

    print("ObjectId:")
    print(str(object_ids[0]))
    return str(object_ids[0])