"""
Pydantic models for request bodies, ensuring clear typing and validation.
"""
from pydantic import BaseModel
from typing import Dict, Any

class GenerateFormRequest(BaseModel):
    company_id: str
    memory_data: Dict[str, Any]

class UpdateFormRequest(BaseModel):
    formData: Dict
    updateCommand: str
