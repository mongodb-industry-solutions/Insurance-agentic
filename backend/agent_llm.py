from langchain_aws import ChatBedrock

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


def get_llm(model_id: str = os.getenv("BEDROCK_MODEL_HAIKU", "anthropic.claude-sonnet-5"),
            aws_access_key: str = os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region: str = os.getenv("AWS_REGION")) -> ChatBedrock:
    """
    Get an instance of the ChatBedrock class for the specified model ID and AWS credentials.

    Args:
        model_id (str): The model ID or inference profile ARN to use.
        aws_access_key (str): The AWS access key ID.
        aws_secret_key (str): The AWS secret access key.
        aws_region (str): The AWS region to use.
    """

    kwargs = dict(
        model=model_id,
        region=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        temperature=0,
    )
    if model_id.startswith("arn:"):
        kwargs["provider"] = "anthropic"

    return ChatBedrock(**kwargs)
