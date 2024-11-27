from typing import List
import csv
import json
import yaml

class SearchTermsLoader:
    """Handles loading search terms from various file formats"""
    
    @staticmethod
    def load_terms(file_path: str) -> List[str]:
        """Load search terms from a file based on its extension"""
        ext = file_path.lower().split('.')[-1]
        
        try:
            if ext == 'txt':
                return SearchTermsLoader._load_txt(file_path)
            elif ext == 'csv':
                return SearchTermsLoader._load_csv(file_path)
            elif ext == 'json':
                return SearchTermsLoader._load_json(file_path)
            elif ext in ('yml', 'yaml'):
                return SearchTermsLoader._load_yaml(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            raise Exception(f"Error loading terms from {file_path}: {str(e)}")

    @staticmethod
    def _load_txt(file_path: str) -> List[str]:
        """Load terms from a text file (one term per line)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def _load_csv(file_path: str) -> List[str]:
        """Load terms from a CSV file"""
        terms = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():  # Use first column
                    terms.append(row[0].strip())
        return terms

    @staticmethod
    def _load_json(file_path: str) -> List[str]:
        """Load terms from a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(term).strip() for term in data if str(term).strip()]
            elif isinstance(data, dict) and 'terms' in data:
                return [str(term).strip() for term in data['terms'] if str(term).strip()]
            raise ValueError("JSON file must contain an array or object with 'terms' key")

    @staticmethod
    def _load_yaml(file_path: str) -> List[str]:
        """Load terms from a YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                return [str(term).strip() for term in data if str(term).strip()]
            elif isinstance(data, dict) and 'terms' in data:
                return [str(term).strip() for term in data['terms'] if str(term).strip()]
            raise ValueError("YAML file must contain an array or object with 'terms' key")