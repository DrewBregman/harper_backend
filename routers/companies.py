# backend/routers/companies.py
from fastapi import APIRouter
from services.memory_service import get_companies, get_company_memory

router = APIRouter()

@router.get("/", summary="List available companies")
def list_companies():
    """
    Returns a list of available companies from Retool.
    """
    companies = get_companies()
    return {"companies": companies}

@router.get("/{company_id}/memory", summary="Fetch data/memory for a company")
def fetch_company_memory(company_id: int):
    """
    Returns the memory/data for a selected company from Retool.
    """
    memory_data = get_company_memory(company_id)
    return {"memory": memory_data}
