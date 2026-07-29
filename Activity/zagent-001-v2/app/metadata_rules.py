import os
import re
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

@dataclass
class MetadataRule:
    column_name: str
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    regex_pattern: Optional[str] = None
    nullability: Optional[str] = None

def normalize_key(key: str) -> str:
    """Normalizes keys to ignore casing and non-alphanumeric characters."""
    return "".join(c.lower() for c in key if c.isalnum())

class MetadataRulesManager:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.rules: Dict[str, MetadataRule] = {}
        self.load_rules()

    def load_rules(self) -> None:
        if not os.path.exists(self.metadata_path):
            logger.warning(f"Metadata file not found at path: {self.metadata_path}. Validation will run without loaded rules.")
            return

        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            # Safely replace unquoted NaN values with null using regex
            # e.g., : NaN, , NaN, or [NaN
            cleaned_content = re.sub(r':\s*NaN\b', ': null', raw_content)
            cleaned_content = re.sub(r',\s*NaN\b', ', null', cleaned_content)
            cleaned_content = re.sub(r'\[\s*NaN\b', '[null', cleaned_content)

            raw_rules = json.loads(cleaned_content)
            
            for item in raw_rules:
                col_name = item.get("column_name")
                if not col_name:
                    continue

                norm_name = normalize_key(col_name)
                
                # Extract and parse min_length
                min_el = item.get("minimum_element")
                min_len = None
                if min_el is not None and not (isinstance(min_el, str) and min_el == "NaN"):
                    try:
                        min_len = int(float(min_el))
                    except (ValueError, TypeError):
                        pass

                # Extract and parse max_length
                max_el = item.get("maximum_element")
                max_len = None
                if max_el is not None and not (isinstance(max_el, str) and max_el == "NaN"):
                    try:
                        max_len = int(float(max_el))
                    except (ValueError, TypeError):
                        pass

                # Extract and parse regex
                regex_pat = item.get("regex_pattern")
                if regex_pat == "NaN" or not regex_pat:
                    regex_pat = None

                # Extract and parse nullability
                null_val = item.get("nullability")
                if null_val == "NaN" or not null_val:
                    null_val = None

                self.rules[norm_name] = MetadataRule(
                    column_name=col_name,
                    min_length=min_len,
                    max_length=max_len,
                    regex_pattern=regex_pat,
                    nullability=null_val
                )
                
            logger.info(f"Successfully loaded {len(self.rules)} metadata validation rules from {self.metadata_path}")
        except Exception as e:
            logger.error(f"Error loading metadata validation rules: {str(e)}", exc_info=True)

    def get_rule_for_field(self, field_name: str) -> Optional[MetadataRule]:
        norm_name = normalize_key(field_name)
        # We can also check fuzzy matching if the field has underscores or is camelCase
        # e.g., legal_entity_type -> legalentitytype, which matches normalized key legalentitytype
        return self.rules.get(norm_name)
