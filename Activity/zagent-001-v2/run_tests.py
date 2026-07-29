import sys
import os
import unittest
import json
import logging
from typing import Dict, Any

# Ensure zagent-001-v2 root is in system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import AppConfig, ModelConfig, validate_provider_config
from app.metadata_rules import MetadataRulesManager, normalize_key
from app.intelligence_schema import SchemaManager
from app.validation import ValidationEngine, normalize_value
from app.providers import ProviderAdapter
from app.graph import calculate_overlap, clean_and_parse_json

# Setup basic logging
logging.basicConfig(level=logging.INFO)

class TestZagentComponents(unittest.TestCase):
    def setUp(self):
        # Setup path to metadata
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.metadata_path = os.path.join(self.workspace_dir, "meta_data_complete.json")

    def test_config_loading(self):
        """Test configurations parsing and fallbacks."""
        config = AppConfig(metadata_path=self.metadata_path)
        self.assertEqual(config.app_name, "zagent-001-v2")
        self.assertEqual(config.api_port, 8010)
        self.assertTrue(os.path.exists(config.metadata_path))

        model_cfg = ModelConfig()
        # Ensure validation function returns false if no keys are set
        # Since keys are read from os.environ, let's verify validate_provider_config behavior
        model_cfg.gemini.api_key = ""
        model_cfg.groq.api_key = ""
        model_cfg.openrouter.api_key = ""
        self.assertFalse(validate_provider_config(model_cfg))

        model_cfg.gemini.api_key = "test-key"
        self.assertTrue(validate_provider_config(model_cfg))

    def test_metadata_rules_manager(self):
        """Test metadata parser handles NaNs and key normalization."""
        manager = MetadataRulesManager(self.metadata_path)
        
        # Test key normalization
        self.assertEqual(normalize_key("Company Name"), "companyname")
        self.assertEqual(normalize_key("Countries Operating In"), "countriesoperatingin")
        self.assertEqual(normalize_key("attrition_signal"), "attritionsignal")

        # Test specific rules load
        rule = manager.get_rule_for_field("companyName")
        self.assertIsNotNone(rule)
        self.assertEqual(rule.column_name, "Company Name")
        self.assertEqual(rule.min_length, 2)
        self.assertEqual(rule.max_length, 255)
        self.assertEqual(rule.nullability, "Not Null")

    def test_intelligence_schema_inference(self):
        """Test SchemaManager dynamic build, inference, and counts."""
        manager = SchemaManager()
        admin_count, gen_count, total = manager.totals()
        
        self.assertEqual(admin_count, 13)
        self.assertEqual(gen_count, 152)
        self.assertEqual(total, 165)

        # Test type inferences
        self.assertEqual(manager.fields["websiteUrl"].field_type, "url")
        self.assertEqual(manager.fields["countriesOperatingIn"].field_type, "list")
        self.assertEqual(manager.fields["natureOfCompany"].field_type, "enum")
        self.assertEqual(manager.fields["remote_work_policy"].field_type, "enum")
        self.assertEqual(manager.fields["valuation_estimate"].field_type, "string")
        self.assertEqual(manager.fields["founders"].field_type, "list")

    def test_validation_engine(self):
        """Test Value Normalizer and validation checks."""
        schema_manager = SchemaManager()
        rules_manager = MetadataRulesManager(self.metadata_path)
        engine = ValidationEngine(rules_manager, schema_manager)

        # 1. Normalizer
        self.assertEqual(normalize_value("  OpenAI  ", "string"), "OpenAI")
        self.assertEqual(normalize_value("N/A", "string"), "NA")
        self.assertEqual(normalize_value("", "string"), "NA")
        self.assertEqual(normalize_value("A, B | C ; D", "list"), ["A", "B", "C", "D"])
        self.assertEqual(normalize_value(["A ", "B", "N/A"], "list"), ["A", "B"])

        # 2. Type validation - URL
        val, err = engine.validate_value("https://openai.com", schema_manager.fields["websiteUrl"])
        self.assertIsNone(err)
        self.assertEqual(val, "https://openai.com")

        val, err = engine.validate_value("openai.com", schema_manager.fields["websiteUrl"])
        self.assertIsNotNone(err)

        # 3. Type validation - Year
        val, err = engine.validate_value("2015", schema_manager.fields["yearOfIncorporation"])
        self.assertIsNone(err)

        val, err = engine.validate_value("2500", schema_manager.fields["yearOfIncorporation"])
        self.assertIsNotNone(err) # Out of bounds 1700 - 2100

        # 4. Type validation - Enum
        val, err = engine.validate_value("private", schema_manager.fields["natureOfCompany"])
        self.assertIsNone(err)
        self.assertEqual(val, "Private") # Normalized casing

        val, err = engine.validate_value("UnknownType", schema_manager.fields["natureOfCompany"])
        self.assertIsNotNone(err)

        # 5. Nullability constraint validation
        # companyName has "Not Null" constraint
        val, err = engine.validate_value("NA", schema_manager.fields["companyName"])
        self.assertIsNotNone(err) # Should fail

        # shortName is Nullable
        val, err = engine.validate_value("NA", schema_manager.fields["shortName"])
        self.assertIsNone(err) # Should pass

    def test_consensus_overlap(self):
        """Test calculation of token overlap consistency."""
        context = "OpenAI was founded in 2015 by Sam Altman, Elon Musk and others in San Francisco."
        
        # 100% overlap
        overlap1 = calculate_overlap("Sam Altman", context)
        self.assertEqual(overlap1, 1.0)
        
        # 50% overlap (words >= 3 chars: "sam" is in context, "xyz" is not)
        overlap2 = calculate_overlap("Sam Xyz", context)
        self.assertEqual(overlap2, 0.5)

        # 0% overlap
        overlap3 = calculate_overlap("Xyz Abc", context)
        self.assertEqual(overlap3, 0.0)

    def test_json_clean_parse(self):
        """Test parsing robustly cleans Markdown wrapping tags."""
        raw_json_block = """
        Here is the JSON you requested:
        ```json
        {
            "founders": ["Sam Altman", "Greg Brockman"],
            "legal_entity_type": "LLC"
        }
        ```
        """
        parsed = clean_and_parse_json(raw_json_block)
        self.assertEqual(parsed.get("legal_entity_type"), "LLC")
        self.assertEqual(len(parsed.get("founders", [])), 2)

if __name__ == "__main__":
    unittest.main()
