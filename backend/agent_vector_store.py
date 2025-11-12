from langchain_mongodb import MongoDBAtlasVectorSearch

from langchain_aws import BedrockEmbeddings
from embeddings.bedrock.getters import get_embedding_model

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


def create_vector_store(
    cluster_uri: str,
    database_name: str,
    collection_name: str,
    text_key: str,
    embedding_key: str,
    embedding_model: BedrockEmbeddings,
    index_name: str = None,
) -> MongoDBAtlasVectorSearch:
   

    # Vector Store Creation
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=cluster_uri,
        namespace=database_name + "." + collection_name,
        embedding=embedding_model,
        embedding_key=embedding_key,
        index_name=index_name,
        text_key=text_key,
    )

    return vector_store


def lookup_collection(vector_store: MongoDBAtlasVectorSearch, query: str, n=1) -> str:
    result = vector_store.similarity_search_with_score(query=query, k=n)
    #return str(result[0][0].page_content)
    return str(result)
    
