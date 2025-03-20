import pandas as pd
import json
from fastapi import UploadFile
from typing import List, Dict

class MetadataExtractor:
    @staticmethod
    async def extract_metadata(files: List[UploadFile]) -> Dict:
        metadata = {}

        for file in files:
            file_metadata = {}
            file_extension = file.filename.split(".")[-1].lower()

            if file_extension == "xlsx":
                df = pd.read_excel(file.file)
            elif file_extension == "json":
                try:
                    data = json.load(file.file)
                    df = pd.json_normalize(data, sep=".")
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid JSON format in file: {file.filename}")
            elif file_extension == "csv":
                df = pd.read_csv(file.file)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            file_metadata["columns"] = [
                {"column_name": col, "data_type": str(df[col].dtype), "sample_values": df[col].dropna().tolist()[:50]}
                for col in df.columns
            ]

            metadata[file.filename] = file_metadata

        return metadata
