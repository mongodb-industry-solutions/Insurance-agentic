from embeddings.bedrock.client import BedrockClient
from langchain_aws import BedrockEmbeddings

from dotenv import load_dotenv
import os

import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Load environment variables from .env file
load_dotenv()

# Getting Bedrock Client
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
bedrock_client = BedrockClient(
    aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)._get_bedrock_client()


def get_embedding_model(model_id: str) -> BedrockEmbeddings:

    # Initialize BedrockEmbeddings with AWS credentials and region
    embedding_model = BedrockEmbeddings(
        client=bedrock_client,
        model_id=model_id
    )

    return embedding_model


def get_embedding(text: str, model_id: str) -> BedrockEmbeddings:
    """Generate an embedding for the given text using Bedrock Cohere English Embeddings."""

    # Check for valid input
    if not text or not isinstance(text, str):
        logging.error("Invalid input. Please provide a valid text input.")
        return None

    # Initialize BedrockEmbeddings with AWS credentials and region
    embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id=model_id
    )

    try:
        # Call the predict method to generate embeddings
        embedding = embeddings.embed_documents([text])[0]
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None


# Example usage
if __name__ == '__main__':

    # Example text
    text = "Embed this text."
    model_id = "cohere.embed-english-v3"

    # Generate embedding
    embedding = get_embedding(text=text, model_id=model_id)
    print(embedding)