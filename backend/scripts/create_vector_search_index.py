"""
Idempotent creation of the MongoDB Vector Search index that
agent_tools.py's fetch_guidelines() depends on (INDEX_NAME =
"description_index"). Run this once against the policy_documents
collection before relying on guideline lookups.

Usage:
    poetry run python scripts/create_vector_search_index.py
"""

import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

INDEX_NAME = "description_index"
VECTOR_FIELD = "descriptionEmbedding"
DIMENSIONS = 1024
SIMILARITY_METRIC = "cosine"


def create_index(
    index_name: str = INDEX_NAME,
    vector_field: str = VECTOR_FIELD,
    dimensions: int = DIMENSIONS,
    similarity_metric: str = SIMILARITY_METRIC,
) -> dict:
    cluster_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    client = MongoClient(cluster_uri, appName="insurance-agentic")
    collection = client[database_name][collection_name]

    index_config = {
        "name": index_name,
        "type": "vectorSearch",
        "definition": {
            "fields": [
                {
                    "path": vector_field,
                    "type": "vector",
                    "numDimensions": dimensions,
                    "similarity": similarity_metric,
                }
            ]
        },
    }

    logger.info(f"Collection: {database_name}.{collection_name}")
    logger.info(f"Vector Field: {vector_field}")
    logger.info(f"Dimensions: {dimensions}")
    logger.info(f"Similarity Metric: {similarity_metric}")

    try:
        collection.create_search_index(index_config)
        logger.info(f"Vector search index '{index_name}' created successfully.")
        return {"status": "success", "message": f"Vector search index '{index_name}' created successfully."}
    except OperationFailure as e:
        if e.code == 68:  # IndexAlreadyExists
            logger.info(f"Vector search index '{index_name}' already exists.")
            return {"status": "info", "message": f"Vector search index '{index_name}' already exists."}
        logger.error(f"Error creating vector search index: {e}")
        return {"status": "error", "message": f"Error creating vector search index: {e}"}


if __name__ == "__main__":
    result = create_index()
    print(result)
