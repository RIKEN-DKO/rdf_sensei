
import os
import json
import re
from typing import List, Dict, Tuple

class DataLoader:
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        self.data = []

    def load_data(self):
        # Load all JSON files from the directory
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f"Loading data from {file_path}")
                    data = json.load(f)
                    self.data.extend(data)

    def preprocess_questions(self) -> List[Tuple[str, Dict]]:
        # Extract and preprocess questions
        processed_data = []
        for item in self.data:
            questions = item.get('questions', [])
            high_rating_questions = [
                q for q in questions if q.get('rating', 0) > 0
            ]
            if not high_rating_questions:
                continue  # Skip if all questions have rating 0

            for q in high_rating_questions:
                question_text = q['question']
                # Remove entities marked with <<>>
                # cleaned_question = re.sub(r'<<.*?>>', '', question_text)
                # cleaned_question = cleaned_question.strip()
                # Remove initial numbers
                cleaned_question = re.sub(r'^\d+\.?\s*', '', question_text).strip()
                # Store the cleaned question and associated data
                entity_mapping = item.get('entity_mapping', {})

                # Clean entity keys by removing surrounding non-word characters and extracting
                #  the entity name from <<>> markers
                new_entity_mapping = {
                    re.sub(r'^[^\w]+|[^\w]+$', '', re.sub(r'<<(.+?)>>', r'\1', k)).strip(): v
                    for k, v in entity_mapping.items()
                }

                processed_data.append((cleaned_question, {
                    'original_question': cleaned_question,
                    'sparql_query': item.get('sparql_query'),
                    # Add entity mapping to the processed data
                    'entity_mapping': new_entity_mapping
                }))
        return processed_data