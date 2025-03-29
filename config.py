# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
LLAMA_PARSE_API_KEY = os.getenv('LLAMA_PARSE_API_KEY')
ANVIL_API_KEY = os.getenv('ANVIL_API_KEY')

# API URLs
COMPANIES_API_URL = os.getenv('COMPANIES_API_URL')
COMPANY_MEMORY_API_URL = os.getenv('COMPANY_MEMORY_API_URL')
ANVIL_BASE_URL = os.getenv('ANVIL_BASE_URL')

# Retool Configuration
RETOOL_COMPANY_LIST_KEY = os.getenv('RETOOL_COMPANY_LIST_KEY')
RETOOL_COMPANY_MEMORY_KEY = os.getenv('RETOOL_COMPANY_MEMORY_KEY')

# Anvil Configuration
ANVIL_TEMPLATE_EID = os.getenv('ANVIL_TEMPLATE_EID')
ANVIL_ORGANIZATION_EID = os.getenv('ANVIL_ORGANIZATION_EID')

RETOOL_COMPANY_LIST_URL = os.getenv("RETOOL_COMPANY_LIST_URL", "https://tatch.retool.com/url/company-query")
RETOOL_COMPANY_MEMORY_URL = os.getenv("RETOOL_COMPANY_MEMORY_URL", "https://tatch.retool.com/url/company-memory")

# property something called applicant etc
# part time employees