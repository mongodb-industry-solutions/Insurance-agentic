"""
Seeds the policy_documents collection with sample insurance guideline
documents, embedding each with the same Cohere model agent_tools.py's
fetch_guidelines() searches against (cohere.embed-english-v3, via
embeddings/bedrock/getters.get_embedding_model). Without this, guideline
lookup silently returns no results (confirmed: an empty collection makes
vector_store.similarity_search_with_score() return [], which fetch_guidelines()
then indexes into and raises IndexError).

Idempotent: skips documents whose description text is already present in
the collection.

Usage:
    poetry run python scripts/create_vector_search_index.py  # create the index first
    poetry run python scripts/seed_policy_documents.py
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from embeddings.bedrock.getters import get_embedding_model

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SAMPLE_GUIDELINES = [
    {
        "title": "Tire Damage Coverage",
        "description": (
            "Flat tires, punctures, and blowouts caused by road hazards (nails, "
            "glass, potholes) are covered under comprehensive or roadside "
            "assistance policy sections, subject to the policyholder's "
            "deductible. Damage from normal wear and tear or manufacturer "
            "defects is not covered and should be directed to the tire "
            "manufacturer's warranty instead."
        ),
    },
    {
        "title": "Collision Damage Coverage",
        "description": (
            "Vehicle damage resulting from a collision with another vehicle or "
            "object is covered under collision coverage. The claim handler must "
            "verify fault determination, obtain a repair estimate from an "
            "authorized body shop, and confirm the policyholder's deductible "
            "before authorizing repairs."
        ),
    },
    {
        "title": "Windshield and Glass Damage Coverage",
        "description": (
            "Cracked or shattered windshields and windows caused by road debris, "
            "weather, or vandalism are covered under comprehensive glass "
            "coverage, often with a reduced or waived deductible depending on "
            "the policy. Full replacement is recommended when a crack exceeds "
            "the size of a dollar bill or obstructs the driver's line of sight."
        ),
    },
    {
        "title": "Weather and Natural Disaster Damage Coverage",
        "description": (
            "Damage from hail, flooding, falling trees, or other natural events "
            "is covered under comprehensive coverage. Claim handlers should "
            "document the extent of exterior and interior damage, confirm the "
            "event date against regional weather reports, and check for a "
            "regional catastrophe declaration that may affect claim processing "
            "timelines."
        ),
    },
    {
        "title": "Theft and Vandalism Coverage",
        "description": (
            "Vehicle theft, attempted theft, and vandalism (broken windows, "
            "keying, stolen parts) are covered under comprehensive coverage. A "
            "police report is required before a claim can be processed. Claim "
            "handlers should verify the report number and confirm the vehicle's "
            "recovery status before authorizing payout."
        ),
    },
]


def seed(sample_guidelines=SAMPLE_GUIDELINES) -> dict:
    cluster_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_NAME")

    client = MongoClient(cluster_uri, appName="devrel-demo-vectorsearch-langgraph-insurance")
    collection = client[database_name][collection_name]

    embedding_model = get_embedding_model(model_id="cohere.embed-english-v3")

    inserted, skipped = 0, 0
    for doc in sample_guidelines:
        if collection.find_one({"description": doc["description"]}):
            skipped += 1
            continue

        embedding = embedding_model.embed_query(doc["description"])
        collection.insert_one({
            "title": doc["title"],
            "description": doc["description"],
            "descriptionEmbedding": embedding,
        })
        inserted += 1
        logger.info(f"Inserted guideline: {doc['title']}")

    logger.info(f"Done. Inserted: {inserted}, skipped (already present): {skipped}")
    return {"inserted": inserted, "skipped": skipped}


if __name__ == "__main__":
    result = seed()
    print(result)
