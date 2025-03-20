class GenPrompt:
    @staticmethod
    def generate_openai_prompt(metadata, existing_tables):
        prompt = """
        You are an expert in ontology modeling and structured relationship detection.
        Your task is to analyze metadata of multiple tables and generate relationships between them.
        ---
        ## **Dataset Overview**
        The dataset contains the following tables:
        """

        for table_name, table_info in metadata.items():
            prompt += f"### 🗂 Table: {table_name}\n"
            prompt += "**Columns:**\n"
            for column in table_info["columns"]:
                prompt += f"- {column['column_name']} ({column['data_type']}) → Sample Values: {column['sample_values']}\n"

        if existing_tables:
            prompt += "\n### **Existing Tables in Neo4j:**\n"
            for table in existing_tables:
                prompt += f"- {table}\n"

        prompt += """
                    ---  
                    ## **Task Instructions**  
                    You are generating an ontology for a relational database based on the provided table metadata.  
                    Your goal is to **identify table structures, classify columns, and define relationships** dynamically.  

                    ### **1. Identify Table Structures**  
                    - Each **table** is a **node**.  
                    - Each table must have a **label** matching its name.  
                    - Each **column** must be categorized as one of the following:  
                      - `PRIMARY_KEY`: If the column uniquely identifies records in the table.  
                      - `FOREIGN_KEY`: If the column appears in multiple tables and references another table's `PRIMARY_KEY`.  
                      - `ATTRIBUTE`: If the column contains general data (text, numbers, dates, etc.).  
                      - `HIGH_CORRELATION`: If two numeric columns have a **Pearson correlation coefficient > 0.9**.  
                      - `DEPENDENCY`: If two categorical columns define each other (e.g., "State" and "Country").  
                      - `MANY_TO_MANY`: If a table is a **bridge table** (i.e., it connects two tables in a many-to-many relationship).  

                    ### **2. Identify Relationships Between Tables**  
                    - **Foreign Key Relationships**: If a column in one table matches a `PRIMARY_KEY` in another table, classify it as `FOREIGN_KEY`.  
                    - **Correlation-Based Relationships**: If two numerical columns across tables have a **Pearson correlation > 0.9**, classify it as `HIGH_CORRELATION`.  
                    - **Categorical Dependencies**: If two categorical columns (text-based) define each other, classify them as `DEPENDENCY`.  
                    - **Many-to-Many Relationships**: If a table contains only two `FOREIGN_KEY` columns linking two other tables, classify it as `MANY_TO_MANY`.  

                    ### **3. Return the Results in the Following JSON Format**  
                    ```json
                    {
                      "nodes": [
                        {
                          "table": "<table_name>",
                          "label": "<table_name>",
                          "columns": [
                            { 
                              "name": "<column_name>", 
                              "type": "PRIMARY_KEY or FOREIGN_KEY or ATTRIBUTE or HIGH_CORRELATION or DEPENDENCY or MANY_TO_MANY", 
                              "values": ["<sample_value1>", "<sample_value2>", "<sample_value3>"] 
                            }
                          ]
                        }
                      ],
                      "relationships": [
                        {
                          "start_node": "<table_name>",
                          "start_column": "<column_name>",
                          "end_node": "<table_name>",
                          "end_column": "<column_name>",
                          "type": "FOREIGN_KEY or HIGH_CORRELATION or DEPENDENCY or MANY_TO_MANY",
                          "reason": "<explanation_of_relationship>"
                        }
                      ]
                    }
                    ```
                    - Each `Column` node must include a `values` array with **sample row values** for that column.
                    - The `values` field should be limited to **a maximum of 5 unique values** from the dataset for readability.
                    - If a column has a **large number of distinct values**, prioritize the most frequent or representative samples.
                    """

        return prompt
