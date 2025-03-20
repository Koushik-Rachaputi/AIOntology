from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jConnection:
    def __init__(self):
        try:
            self._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            print("Neo4j connection established successfully.")
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            self._driver = None  # Prevent further errors if connection fails

    def close(self):
        if self._driver:
            self._driver.close()

    def query(self, query, parameters=None):
        if not self._driver:
            raise Exception("Neo4j driver is not initialized!")
        with self._driver.session() as session:
            return session.run(query, parameters).data()

neo4j_conn = Neo4jConnection()
