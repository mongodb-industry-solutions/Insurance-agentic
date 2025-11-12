from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent_llm import get_llm
from agent_tools import tools


llm = get_llm(model_id="anthropic.claude-3-haiku-20240307-v1:0")

def create_agent(llm, tools, system_message: str):
    """Create an agent

    Args:
        llm (ChatBedrock): The ChatBedrock instance to use.
        tools (List[Callable]): The list of tools to bind to the agent.
        system_message (str): The system message to display to the agent.

    Returns:
        ChatAgent: The created ChatAgent instance.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a claim handler assistant for an insurance company. Your goal is to help claim handlers understand the scope of the current claim"
                "and provide relevant information to help them make an informed decision. In particular, based on the description of the accident, you need to fetch"
                "and summarize relevant insurance guidelines so that the handler can determine the coverage and process the claim accordingly."
                "Present your findings in a clear and extremely concise manner."
                "Do not add any unnecessary information."
                "You have access to the following tools: {tool_names}, that helps you find relevant insurance guidelines based on the description of the accident."
                "clean the chat history in the database using the clean_chat_history tool"
                "At the end persist data in the database using one of the tools."
                "the document you persist must contain the following fields:"
                "date: the current date and time in iso format"
                "description: a summary of the accident"
                "recommendation: the recommended course of action based on the retrieved guidelines and what happened in the accident (don't inlcude mentions of the claim adjuster)"
                "use bullet points for the recommendation"
                "claim_handler: the name of the claim handler, make one up"
                "Lastly, clean the chat history in the database using the clean_chat_history tool and prefix your response with FINAL ANSWER to indicate the end of your workflow."
                "{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(time=lambda: str(datetime.now()))
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    return prompt | llm.bind_tools(tools)


# Chatbot agent and node
chatbot_agent = create_agent(
    llm,
    tools,
    system_message="Edit this message.",
)