# forms.py
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Dict, Any
from collections import defaultdict
import copy, os
import openai
from config import OPENAI_API_KEY
import tempfile

router = APIRouter()

openai.api_key = OPENAI_API_KEY

# Global in-memory store of form states
# e.g. FORM_STATES[company_id]["current"] => current form data
#      FORM_STATES[company_id]["history"] => stack of old states
FORM_STATES = defaultdict(lambda: {
    "history": [],
    "current": None
})

# Pydantic models
class GenerateFormRequest(BaseModel):
    company_id: int
    memory_data: Dict[str, Any]

class UpdateFormRequest(BaseModel):
    company_id: int
    command: str

@router.post("/generate")
def generate_form_endpoint(request: GenerateFormRequest):
    """
    Generate initial form data from memory_data, store in 'current'.
    Return a pdf_url or any reference if you generate a PDF file.
    """
    initial_form = generate_form_dict(request.company_id, request.memory_data)

    # Clear old data and set new
    FORM_STATES[request.company_id]["history"].clear()
    FORM_STATES[request.company_id]["current"] = initial_form

    # Optionally generate a PDF file for the user
    pdf_url = generate_pdf_and_save(request.company_id, initial_form)
    return {"pdf_url": pdf_url}

@router.post("/update")
def update_form_endpoint(request: UpdateFormRequest):
    """
    Applies a text-based command to the current form.
    Moves the old state into 'history' for undo.
    """
    state = FORM_STATES[request.company_id]
    if state["current"] is None:
        raise HTTPException(status_code=400, detail="No form state for this company.")

    # Save old
    old_state = copy.deepcopy(state["current"])
    state["history"].append(old_state)

    # Apply command
    updated_form = apply_command_logic(state["current"], request.command)
    state["current"] = updated_form

    return {"updatedFormData": updated_form}

@router.post("/undo/{company_id}")
def undo_form_endpoint(company_id: int):
    """
    Reverts the form to the previous version if available.
    """
    state = FORM_STATES[company_id]
    if not state["history"]:
        raise HTTPException(status_code=400, detail="No older version to revert to.")

    last_version = state["history"].pop()
    state["current"] = last_version
    return {"updatedFormData": last_version}

#
# Optional: Real /forms/transcribe route for OpenAI Whisper
#
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Example endpoint to accept an audio file and run OpenAI Whisper to transcribe.
    Returns { "transcript": "... recognized text ..." }
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Transcribe with Whisper
        resp = openai.Audio.transcribe(
            model="whisper-1",
            file=open(tmp_path, "rb")
        )
        recognized_text = resp.get("text", "")

        os.remove(tmp_path)
        return {"transcript": recognized_text}

    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

#
# Helper functions
#

def generate_form_dict(company_id: int, memory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example: merges memory_data into a basic dict.
    """
    company_section = memory_data.get("company", {})
    return {
        "agency": "ABC Insurance",
        "applicantName": company_section.get("company_name", ""),
        "contactInformationPrimary": company_section.get("company_primary_email", ""),
        "annualRevenues": str(company_section.get("company_annual_revenue_usd", "")),
        "deductible": ""
    }

def generate_pdf_and_save(company_id: int, form_fields: Dict[str, Any]) -> str:
    """
    Stub: merges `form_fields` into a PDF, writes it to static/forms/.
    Return the path e.g. "/static/forms/form_123.pdf".
    """
    # Generate or fetch your PDF bytes here...
    # For the example, we skip actual PDF generation logic
    return f"/static/forms/form_{company_id}.pdf"

def apply_command_logic(current_form: Dict[str, Any], command: str) -> Dict[str, Any]:
    """
    Very naive approach to interpret the command text and modify fields.
    You can expand with advanced parsing or LLMs.
    """
    cmd = command.lower()
    if "deductible" in cmd:
        current_form["deductible"] = "$5000"
    if "applicant name" in cmd:
        current_form["applicantName"] = "Acme Inc"
    if "annual revenue" in cmd:
        current_form["annualRevenues"] = "5000000"  # example
    if "undo" in cmd:
        # We won't do anything here; user can just call /undo
        pass

    return current_form
