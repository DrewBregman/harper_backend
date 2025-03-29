"""
Service for fetching companies and their memory/data from a data store or external API.
This version calls 'parse_and_clean_memory' to remove phone_events & md before returning.
"""

import requests
import os
from config import (
    RETOOL_COMPANY_LIST_KEY,
    RETOOL_COMPANY_MEMORY_KEY,
    RETOOL_COMPANY_LIST_URL,
    RETOOL_COMPANY_MEMORY_URL
)
from services.parse_memory_service import parse_memory_data
from services.clean_memory_service import clean_memory

def get_companies():
    """
    Fetch the list of companies by calling the Retool "company-query" endpoint.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Workflow-Api-Key": RETOOL_COMPANY_LIST_KEY
    }
    data = {}  # If the endpoint requires additional data, add it here

    try:
        response = requests.post(RETOOL_COMPANY_LIST_URL, json=data, headers=headers)
        response.raise_for_status()
        # The response should be a list of companies
        company_list = response.json()
        return company_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching companies: {e}")
        return []

def get_company_memory(company_id: int):
    """
    Fetch the memory/data for a specific company by calling the Retool "company-memory" endpoint,
    then parse & clean it to remove phone_events and md.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Workflow-Api-Key": RETOOL_COMPANY_MEMORY_KEY
    }
    data = {
        "company_id": company_id
    }

    try:
        response = requests.post(RETOOL_COMPANY_MEMORY_URL, json=data, headers=headers)
        response.raise_for_status()
        # Parse the raw memory JSON
        memory_data = response.json()
        # Clean out phone_events & md
        cleaned_data = clean_memory(memory_data)
        return cleaned_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching company memory: {e}")
        return {}
