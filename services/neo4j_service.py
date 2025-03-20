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
        """Store ontology in Neo4j while preventing duplicate nodes, relationships, and ensuring only table-to-table connections."""
        try:
            existing_tables = Neo4jService.get_existing_tables()
            if isinstance(existing_tables, dict) and "error" in existing_tables:
                return existing_tables  # Return error message if fetching tables failed

            # Step 1: Ensure all Table nodes are created (Check before inserting)
            for node in ontology.get("nodes", []):
                table_name = node["label"]
                if table_name not in existing_tables:  # Only create if not exists
                    neo4j_conn.query("""
                        MERGE (t:Table {name: $name})
                    """, {"name": table_name})

            # Step 2: Ensure Column nodes are created and linked to their respective Table nodes
            for node in ontology.get("nodes", []):
                table_name = node["label"]
                for column in node.get("columns", []):
                    column_name = column["name"]
                    column_type = column["type"]
                    new_values = set(column.get("values", []))  # Convert list to set for comparison

                    # Fetch existing values for the column (if it exists)
                    existing_col = neo4j_conn.query("""
                        MATCH (c:Column {name: $col_name}) RETURN c.values AS values
                    """, {"col_name": column_name})

                    existing_values = set(existing_col[0]["values"]) if existing_col and "values" in existing_col[0] else set()

                    # Merge only if the column does not already exist
                    neo4j_conn.query("""
                        MERGE (c:Column {name: $col_name, type: $col_type})
                        WITH c
                        MATCH (t:Table {name: $table_name})
                        MERGE (t)-[:HAS_COLUMN]->(c)
                    """, {
                        "col_name": column_name,
                        "col_type": column_type,
                        "table_name": table_name
                    })

                    # Only update values if new ones are detected
                    if not new_values.issubset(existing_values):
                        updated_values = list(existing_values.union(new_values))
                        neo4j_conn.query("""
                            MATCH (c:Column {name: $col_name})
                            SET c.values = $values
                        """, {
                            "col_name": column_name,
                            "values": updated_values
                        })

            # Step 3: Ensure table-to-table relationships (avoid duplicates)
            existing_tables = Neo4jService.get_existing_tables()

            for rel in ontology.get("relationships", []):
                start_node = rel["start_node"]
                end_node = rel["end_node"]

                # Ensure both nodes exist and avoid duplicate relationships
                if start_node in existing_tables and end_node in existing_tables:
                    existing_rel = neo4j_conn.query("""
                        MATCH (t1:Table {name: $start_node})-[r:CONNECTED_TO]->(t2:Table {name: $end_node})
                        RETURN COUNT(r) AS rel_count
                    """, {
                        "start_node": start_node,
                        "end_node": end_node
                    })

                    # Only create relationship if it doesn't already exist
                    if existing_rel[0]["rel_count"] == 0:
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

            return {"message": "Ontology updated successfully with duplicate checks in place"}

        except Exception as e:
            return {"error": str(e)}
         

