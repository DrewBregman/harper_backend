"""
Service for interacting with Anvil's PDF filling API.
"""
import os
from python_anvil.api import Anvil
from config import ANVIL_API_KEY

def fill_pdf_with_anvil(data: dict) -> bytes:
    """
    Sends JSON data to Anvil to fill a PDF or generate a form.
    Returns the PDF bytes that can be written to a file.
    """
    template_id = '7VCXZAolDIPToVLh3O3O'  # Our template ID
    anvil = Anvil(api_key=ANVIL_API_KEY)
    
    # Fill the PDF with the provided data
    pdf_bytes = anvil.fill_pdf(template_id, data)
    return pdf_bytes
