from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from services.openai_service import AzureOpenAIClient, extract_json
from services.neo4j_service import Neo4jService
from services.metadata_service import MetadataExtractor
from services.prompt_service import GenPrompt

router = APIRouter()

# Initialize OpenAI Client
azure_openai_client = AzureOpenAIClient()

@router.post("/data/ingest")
async def ingest(files: List[UploadFile] = File(...), database_name: str = Form(...)):
    try:
        metadata = await MetadataExtractor.extract_metadata(files)
        existing_tables = Neo4jService.get_existing_tables()

        prompt = GenPrompt.generate_openai_prompt(metadata, existing_tables)
        response = azure_openai_client.send_prompt(prompt)
        ontology = extract_json(response)

        store_result = Neo4jService.store_ontology(ontology)

        return {
            "message": "Metadata processed successfully",
            "database": database_name,
            "existing_tables": existing_tables,
            "metadata": metadata,
            "response": response,
            "ontology": ontology,
            "store_result": store_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
