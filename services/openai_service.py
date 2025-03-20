import openai
import config
import json
import re

class AzureOpenAIClient:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = config.AZURE_OPENAI_ENDPOINT
        openai.api_key = config.OPENAI_API_KEY
        openai.api_version = "2024-02-01"
        self.deployment_name = config.DEPLOYMENT_NAME

    def send_prompt(self, prompt):
        """Send a prompt to Azure OpenAI and return response."""
        try:
            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert in ontology modeling and structured relationship detection."},
                    {"role": "system", "content": "Give result as JSON as per the prompt."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"


# Move extract_json outside the class
def extract_json(response):
    """Extract JSON content from OpenAI response."""
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        json_content = match.group(0)
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No valid JSON found.")
        return None
