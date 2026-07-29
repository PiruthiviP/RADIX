import re
import logging
from urllib.parse import urlparse
from typing import Any, Dict, Tuple, Optional

from app.intelligence_schema import FieldSpec, SchemaManager
from app.metadata_rules import MetadataRulesManager, MetadataRule

logger = logging.getLogger(__name__)

def normalize_value(val: Any, field_type: str) -> Any:
    """
    Cleans strings: strips whitespace. Maps variants of empty strings ("" or "N/A" etc.) to "NA".
    For lists: if a string is provided, splits by delimiters and strips items.
    """
    if val is None:
        return "NA" if field_type != "list" else []

    if field_type == "list":
        if isinstance(val, str):
            # Split by commas, semicolons, or pipes
            parts = re.split(r'[,;|]', val)
            cleaned_list = []
            for p in parts:
                p_stripped = p.strip()
                if p_stripped and p_stripped.lower() not in ["", "n/a", "na", "not available", "unknown", "nan", "null"]:
                    cleaned_list.append(p_stripped)
            return cleaned_list
        elif isinstance(val, list):
            cleaned_list = []
            for x in val:
                if x is not None:
                    cleaned_str = str(x).strip()
                    if cleaned_str and cleaned_str.lower() not in ["", "n/a", "na", "not available", "unknown", "nan", "null"]:
                        cleaned_list.append(cleaned_str)
            return cleaned_list
        else:
            return []

    # Scalar values (string, url, year, enum)
    if isinstance(val, list):
        val = ", ".join(str(x) for x in val)
        
    val_str = str(val).strip()
    if val_str.lower() in ["", "n/a", "na", "not available", "unknown", "nan", "null"]:
        return "NA"
    return val_str

class ValidationEngine:
    def __init__(self, rules_manager: MetadataRulesManager, schema_manager: SchemaManager):
        self.rules_manager = rules_manager
        self.schema_manager = schema_manager

    def validate_value(self, val: Any, spec: FieldSpec) -> Tuple[Any, Optional[str]]:
        """
        Normalizes a value, checks type constraints and metadata rules.
        Returns a tuple of (normalized_value, error_message_or_none).
        """
        value = normalize_value(val, spec.field_type)
        rule = self.rules_manager.get_rule_for_field(spec.name)

        # 1. Nullability Check
        if spec.field_type == "list":
            is_empty = len(value) == 0
            if is_empty:
                if rule and rule.nullability == "Not Null":
                    return value, f"Field '{spec.name}' is not nullable but got empty list."
                return value, None
        else:
            if value == "NA":
                if rule and rule.nullability == "Not Null":
                    return value, f"Field '{spec.name}' is not nullable but got 'NA'."
                return value, None

        # 2. Scalar Type Check
        if spec.field_type in ["string", "url", "year", "enum"]:
            if not isinstance(value, str):
                return value, f"Field '{spec.name}' expected string, got {type(value).__name__}."

        # 3. Specific Type Validations
        if spec.field_type == "url":
            try:
                parsed = urlparse(value)
                if not (parsed.scheme in ["http", "https"] and parsed.netloc):
                    return value, f"Field '{spec.name}' has invalid URL value: '{value}'."
            except Exception:
                return value, f"Field '{spec.name}' has invalid URL value: '{value}'."

        elif spec.field_type == "year":
            if not re.match(r'^\d{4}$', value):
                return value, f"Field '{spec.name}' expected 4-digit year, got '{value}'."
            try:
                year_num = int(value)
                if not (1700 <= year_num <= 2100):
                    return value, f"Field '{spec.name}' year {year_num} is out of bounds [1700, 2100]."
            except ValueError:
                return value, f"Field '{spec.name}' has invalid year: '{value}'."

        elif spec.field_type == "enum":
            if spec.enum_values:
                # Case-insensitive match check and normalize value casing to match enum
                matched = False
                for ev in spec.enum_values:
                    if ev.lower() == value.lower():
                        value = ev
                        matched = True
                        break
                if not matched:
                    return value, f"Field '{spec.name}' value '{value}' is not in allowed enums: {spec.enum_values}."

        # 4. Metadata Rules Checks (Lengths & Regex)
        if rule:
            val_len = len(value) # Character count for str, Element count for list
            
            # String or List Length bounds
            if rule.min_length is not None and val_len < rule.min_length:
                return value, f"Field '{spec.name}' size {val_len} is less than min_length {rule.min_length}."
            if rule.max_length is not None and val_len > rule.max_length:
                return value, f"Field '{spec.name}' size {val_len} is greater than max_length {rule.max_length}."

            # Regex Match
            if rule.regex_pattern and isinstance(value, str):
                try:
                    # Let's ensure rule regex matches
                    if not re.search(rule.regex_pattern, value):
                        return value, f"Field '{spec.name}' value '{value}' does not match regex rule: {rule.regex_pattern}."
                except Exception as e:
                    logger.warning(f"Error applying regex constraint '{rule.regex_pattern}' on field '{spec.name}': {str(e)}")

        return value, None

    def validate_dataset(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Validates all fields defined in the schema manager.
        Returns a tuple of (valid_dataset_dict, failed_fields_dict).
        """
        valid_dict = {}
        failed_dict = {}

        for field_name, spec in self.schema_manager.fields.items():
            # Get raw value from dict, mapping camelCase or snake_case key
            val = data.get(field_name)
            if val is None:
                # Try camelCase equivalent for admin fields
                camel_name = field_name
                # e.g., companyName in schema, check if it exists
                # In intelligence_schema we define admin fields as camelCase already.
                # In generated fields we use snake_case.
                # So let's look up by exact key
                pass

            norm_val, err_msg = self.validate_value(val, spec)
            if err_msg:
                failed_dict[field_name] = err_msg
            else:
                valid_dict[field_name] = norm_val

        return valid_dict, failed_dict
