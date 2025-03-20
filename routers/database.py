from fastapi import APIRouter
from services.neo4j_service import Neo4jService

router = APIRouter(prefix="/database", tags=["Database"])

@router.post("/create/{db_name}")
def create_database(db_name: str):
    return {"message": "Neo4j Community Edition supports only the default database 'neo4j'. Use it instead of creating a new one."}

@router.get("/list")
def list_databases():
    return Neo4jService.fetch_databases()

@router.delete("/delete/{db_name}")
def delete_database(db_name: str):
    return {"message": "Neo4j Community Edition does not support deleting databases."}


@router.delete("/clear")
def clear_database():
    return Neo4jService.clear_database()


@router.get("/nodes")
def list_nodes():
    return Neo4jService.list_all_nodes()

@router.get("/list_Nodes_with_Relationships")
def list_nodes():
    return Neo4jService.list_all_nodes_with_relationships()
