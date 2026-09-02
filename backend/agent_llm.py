from langchain_aws import ChatBedrockConverse

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_llm(model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            aws_access_key: str = os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region: str = os.getenv("AWS_REGION")) -> ChatBedrockConverse:
    """
    Get an instance of the ChatBedrockConverse class for the specified model ID and AWS credentials.

    Args:
        model_id (str): The model ID to use for the ChatBedrockConverse instance.
        aws_access_key (str): The AWS access key ID.
        aws_secret_key (str): The AWS secret access key.
        aws_region (str): The AWS region to use.
    """

    return ChatBedrockConverse(model=model_id,
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                temperature=0)
