import unittest
from unittest.mock import MagicMock, patch
from validator import PipelineValidator
from consolidation_agent import ConsolidationAgent
from regeneration_loop import RegenerationLoop
from db_writer import DBWriter

class TestPipelineLogic(unittest.TestCase):
    def test_validator_rules(self):
        # 1. Valid company data
        valid_data = {
            "name": "Blinkit",
            "logo_url": "https://blinkit.com/logo.png",
            "category": "Startup",
            "nature_of_company": "Private",
            "headquarters_address": "Gurgaon, India",
            "employee_size": "5,000",
            "website_url": "https://blinkit.com",
            "ceo_name": "Albinder Dhindsa",
            "primary_contact_email": "contact@blinkit.com",
            "incorporation_year": 2013,
            "glassdoor_rating": 3.8,
            "net_promoter_score": 45,
            "yoy_growth_rate": "25%"
        }
        errors = PipelineValidator.validate_company(valid_data)
        self.assertEqual(len(errors), 0, f"Expected 0 errors, got: {errors}")

        # 2. Invalid company data
        invalid_data = {
            "name": "Blinkit",
            "logo_url": "invalid-url",
            "category": "Startup",
            "nature_of_company": "Private",
            "headquarters_address": "Gurgaon, India",
            "employee_size": "5,000",
            "website_url": "https://blinkit.com",
            "ceo_name": "Albinder Dhindsa",
            "primary_contact_email": "not-an-email",
            "incorporation_year": 1750,  # invalid: before 1800
            "glassdoor_rating": 6.5,      # invalid: max 5.0
            "net_promoter_score": 150     # invalid: max 100
        }
        errors = PipelineValidator.validate_company(invalid_data)
        error_fields = [e["field"] for e in errors]
        self.assertIn("logo_url", error_fields)
        self.assertIn("primary_contact_email", error_fields)
        self.assertIn("incorporation_year", error_fields)
        self.assertIn("glassdoor_rating", error_fields)
        self.assertIn("net_promoter_score", error_fields)

    def test_pre_consolidation_logic(self):
        agent = ConsolidationAgent()
        
        # Datasets where Claude and Gemini agree, Llama is NA
        datasets = {
            "claude": {
                "name": "Blinkit",
                "incorporation_year": 2013,
                "ceo_name": "Albinder Dhindsa"
            },
            "gemini": {
                "name": "Blinkit",
                "incorporation_year": 2013,
                "ceo_name": "Albinder" # disagreement
            },
            "llama": {
                "name": "Blinkit",
                "incorporation_year": "NA",
                "ceo_name": "Albinder Dhindsa"
            }
        }
        
        consolidated, conflicts = agent.pre_consolidate(datasets)
        
        # Name and incorporation year should be agreed upon
        self.assertEqual(consolidated["name"], "Blinkit")
        self.assertEqual(consolidated["incorporation_year"], 2013)
        
        # CEO Name has disagreement, should be in conflicts
        self.assertIn("ceo_name", conflicts)
        self.assertEqual(conflicts["ceo_name"]["claude"], "Albinder Dhindsa")
        self.assertEqual(conflicts["ceo_name"]["gemini"], "Albinder")
        self.assertEqual(conflicts["ceo_name"]["llama"], "Albinder Dhindsa")

    @patch('consolidation_agent.ChatOpenAI')
    def test_conflict_resolution(self, mock_chat):
        # Mock consolidation agent LLM response
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"ceo_name": "Albinder Dhindsa"}'
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_llm_instance

        agent = ConsolidationAgent()
        conflicts = {
            "ceo_name": {
                "claude": "Albinder Dhindsa",
                "gemini": "Albinder",
                "llama": "Albinder Dhindsa"
            }
        }
        resolved = agent.resolve_conflicts("Blinkit", conflicts)
        self.assertEqual(resolved.get("ceo_name"), "Albinder Dhindsa")

    @patch('regeneration_loop.ChatOpenAI')
    def test_regeneration_loop(self, mock_chat):
        # Mock regeneration loop LLM response
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "contact@blinkit.com"
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat.return_value = mock_llm_instance

        loop = RegenerationLoop()
        corrected_value = loop.regenerate_field("Blinkit", "primary_contact_email", "invalid-email", "Invalid email address format.")
        self.assertEqual(corrected_value, "contact@blinkit.com")

if __name__ == '__main__':
    unittest.main()
