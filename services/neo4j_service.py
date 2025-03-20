from db.connection import neo4j_conn

class Neo4jService:
    @staticmethod
    def create_database(database_name: str):
         # query = f"CREATE DATABASE {database_name} IF NOT EXISTS"
        # try:
        #     neo4j_conn.query(query)
        #     return {"message": f"Database '{database_name}' created successfully"}
        # except Exception as e:
        #     return {"error": str(e)}
        return {"error": "Neo4j Community Edition supports only one database: 'neo4j'. Please use it instead of creating a new one."}

    @staticmethod
    def fetch_databases():
        query = "SHOW DATABASES"
        try:
            results = neo4j_conn.query(query)
            databases = [db["name"] for db in results]
            return {"databases": databases}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def delete_database(database_name: str):
        # query = f"DROP DATABASE {database_name} IF EXISTS"
        # try:
        #     neo4j_conn.query(query)
        #     return {"message": f"Database '{database_name}' deleted successfully"}
        # except Exception as e:
        #     return {"error": str(e)}
        return {"error": "Neo4j Community Edition does not support deleting databases. Use labels and relationships to organize your data instead."}

    @staticmethod
    def get_existing_tables():
        """Retrieve all stored table names from Neo4j."""
        query = "MATCH (t:Table) RETURN t.name AS table_name"
        try:
            results = neo4j_conn.query(query)
            return [record["table_name"] for record in results]
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def clear_database():
        """Delete all nodes and relationships from the database."""
        try:
            neo4j_conn.query("MATCH (n) DETACH DELETE n")
            return {"message": "Database cleared successfully"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_all_nodes():
        """List all nodes in the database."""
        try:
            results = neo4j_conn.query("MATCH (n) RETURN n")
            nodes = [record["n"] for record in results]
            return {"nodes": nodes}
        except Exception as e:
            return {"error": str(e)}
        
    @staticmethod
    def list_all_nodes_with_relationships():
        """Retrieve all nodes, relationships, and the database name."""
        try:
            # Fetch all nodes
            nodes_result = neo4j_conn.query("MATCH (n:Table) RETURN n.name AS table_name")
            nodes = [record["table_name"] for record in nodes_result]

            # Fetch all relationships
            relationships_result = neo4j_conn.query("""
                MATCH (t1:Table)-[r:CONNECTED_TO]->(t2:Table) 
                RETURN t1.name AS start_node, t2.name AS end_node, r.type AS type, r.reason AS reason
            """)
            relationships = [
                {
                    "start_node": record["start_node"],
                    "end_node": record["end_node"],
                    "type": record["type"],
                    "reason": record["reason"]
                }
                for record in relationships_result
            ]

            return {
                "database": "neo4j",
                "nodes": nodes,
                "relationships": relationships
            }
        except Exception as e:
            return {"error": str(e)}


    # @staticmethod
    # def store_ontology(ontology):
    #     """Store ontology relationships in Neo4j."""
    #     try:
    #         # Ensure all tables (nodes) are created
    #         for node in ontology.get("nodes", []):
    #             neo4j_conn.query("""
    #                 MERGE (t:Table {name: $name})
    #             """, {"name": node["label"]})

    #         # Ensure relationships are created
    #         for rel in ontology.get("relationships", []):
    #             neo4j_conn.query("""
    #                 MERGE (t1:Table {name: $start_node})
    #                 MERGE (t2:Table {name: $end_node})
    #                 MERGE (t1)-[:CONNECTED_TO {type: $type, reason: $reason}]->(t2)
    #             """, {
    #                 "start_node": rel["start_node"].split(".")[0],
    #                 "end_node": rel["end_node"].split(".")[0],
    #                 "type": rel["type"],
    #                 "reason": rel["reason"]
    #             })

    #         return {"message": "Ontology stored successfully"}
        
    #     except Exception as e:
    #         return {"error": str(e)}


    @staticmethod
    def store_ontology(ontology):
        """Store ontology relationships in Neo4j while ensuring proper connections."""
        try:
            existing_tables = Neo4jService.get_existing_tables()
            if isinstance(existing_tables, dict) and "error" in existing_tables:
                return existing_tables  # Return error message if fetching tables failed

            # Ensure all tables (nodes) are created
            for node in ontology.get("nodes", []):
                table_name = node["label"]
                if table_name not in existing_tables:  # Only create if not exists
                    neo4j_conn.query("""
                        MERGE (t:Table {name: $name})
                    """, {"name": table_name})

            # Ensure column nodes are created and linked to tables
            for node in ontology.get("nodes", []):
                table_name = node["label"]
                for column in node.get("columns", []):
                    neo4j_conn.query("""
                        MERGE (c:Column {name: $col_name, type: $col_type})
                        WITH c
                        MATCH (t:Table {name: $table_name})
                        MERGE (t)-[:HAS_COLUMN]->(c)
                    """, {
                        "col_name": column["name"],
                        "col_type": column["type"],
                        "table_name": table_name
                    })

                    # Store sample values as properties of column nodes
                    if "sample_values" in column:
                        neo4j_conn.query("""
                            MATCH (c:Column {name: $col_name})
                            SET c.values = $values
                        """, {
                            "col_name": column["name"],
                            "values": column["sample_values"]
                        })

            # Refresh the existing tables list after inserting new nodes
            existing_tables = Neo4jService.get_existing_tables()

            # Ensure relationships between tables are created
            for rel in ontology.get("relationships", []):
                start_node = rel["start_node"]
                end_node = rel["end_node"]

                # Ensure both nodes exist before creating a relationship
                if start_node in existing_tables and end_node in existing_tables:
                    neo4j_conn.query("""
                        MATCH (t1:Table {name: $start_node})
                        MATCH (t2:Table {name: $end_node})
                        MERGE (t1)-[:CONNECTED_TO {type: $type, reason: $reason}]->(t2)
                    """, {
                        "start_node": start_node,
                        "end_node": end_node,
                        "type": rel["type"],
                        "reason": rel["reason"]
                    })

            return {"message": "Ontology updated successfully with new relationships and column data"}

        except Exception as e:
            return {"error": str(e)}


