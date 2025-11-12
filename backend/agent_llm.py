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


def get_llm(model_id: str = "anthropic.claude-3-haiku-20240307-v1:0", 
            aws_access_key: str = os.getenv("AWS_ACCESS_KEY_ID"), 
            aws_secret_key: str = os.getenv("AWS_SECRET_ACCESS_KEY"), 
            aws_region: str = os.getenv("AWS_REGION")) -> ChatBedrock:
    """
    Get an instance of the ChatBedrock class for the specified model ID and AWS credentials.

    Args:
        model_id (str): The model ID to use for the ChatBedrock instance.
        aws_access_key (str): The AWS access key ID.
        aws_secret_key (str): The AWS secret access key.
        aws_region (str): The AWS region to use.
    """

    return ChatBedrock(model=model_id,
                region=aws_region, 
                aws_access_key_id=aws_access_key, 
                aws_secret_access_key=aws_secret_key,
                temperature=0)
