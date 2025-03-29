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
    try:
        company_id = request.formData.get('company_id')
        state = FORM_STATES[company_id]
        if state["current"] is None:
            raise HTTPException(status_code=400, detail="No form state for this company.")

        # Save old
        old_state = copy.deepcopy(state["current"])
        state["history"].append(old_state)

        # Apply command
        updated_form = apply_command_logic(request.formData, request.updateCommand)
        state["current"] = updated_form

        return {"updatedFormData": updated_form}
    except Exception as e:
        print(f"Error in update_form_endpoint: {str(e)}")
        # If there's an error with the state lookup or form not found,
        # just update the form data directly without state management
        return {"updatedFormData": apply_command_logic(request.formData, request.updateCommand)}

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
    Uses our form generation logic to extract and structure all fields from memory data.
    """
    from logic.form_generation import generate_form
    from services.parse_memory_service import parse_memory_data
    
    # Parse all fields from memory data using Claude
    parsed_data = parse_memory_data(memory_data)
    
    # Convert to the format needed for our forms
    return {
        "billingPlanForPolicyIsDirect": parsed_data.get("billingPlanForPolicyIsDirect", ""),
        "applicantIsLLC": parsed_data.get("applicantIsLLC", ""),
        "dateOfApplication": parsed_data.get("dateOfApplication", ""),
        "agency": parsed_data.get("agency", ""),
        "carrier": parsed_data.get("carrier", ""),
        "naicCode": parsed_data.get("naicCode", ""),
        "companyPolicyOrProgramName": parsed_data.get("companyPolicyOrProgramName", ""),
        "programCode": parsed_data.get("programCode", ""),
        "agencyCustomerId": parsed_data.get("agencyCustomerId", ""),
        "hasBusinessOwnersAttachedSections": parsed_data.get("hasBusinessOwnersAttachedSections", False),
        "hasCommercialGeneralLiabilitySectionsAttached": parsed_data.get("hasCommercialGeneralLiabilitySectionsAttached", False),
        "paymentPlan": parsed_data.get("paymentPlan", ""),
        "methodOfPayment": parsed_data.get("methodOfPayment", ""),
        "audit1": parsed_data.get("audit1", ""),
        "applicantName1": {
            "firstName": parsed_data.get("applicantName1", {}).get("firstName", ""),
            "mi": parsed_data.get("applicantName1", {}).get("mi", ""),
            "lastName": parsed_data.get("applicantName1", {}).get("lastName", "")
        },
        "glCode1": parsed_data.get("glCode1", ""),
        "sic1": parsed_data.get("sic1", ""),
        "naics1": parsed_data.get("naics1", ""),
        "feinOrSocSec1": parsed_data.get("feinOrSocSec1", ""),
        "websiteAddress": {
            "street1": parsed_data.get("websiteAddress", {}).get("street1", ""),
            "street2": parsed_data.get("websiteAddress", {}).get("street2", ""),
            "city": parsed_data.get("websiteAddress", {}).get("city", ""),
            "state": parsed_data.get("websiteAddress", {}).get("state", ""),
            "zip": parsed_data.get("websiteAddress", {}).get("zip", ""),
            "country": parsed_data.get("websiteAddress", {}).get("country", "")
        },
        "contactInformationPrimary1": parsed_data.get("contactInformationPrimary1", ""),
        "contactInformationSecondary1": parsed_data.get("contactInformationSecondary1", ""),
        "premisesZipcode": {
            "street1": parsed_data.get("premisesZipcode", {}).get("street1", ""),
            "street2": parsed_data.get("premisesZipcode", {}).get("street2", ""),
            "city": parsed_data.get("premisesZipcode", {}).get("city", ""),
            "state": parsed_data.get("premisesZipcode", {}).get("state", ""),
            "zip": parsed_data.get("premisesZipcode", {}).get("zip", ""),
            "country": parsed_data.get("premisesZipcode", {}).get("country", "")
        },
        "agencyCustomerId1": parsed_data.get("agencyCustomerId1", ""),
        "location": parsed_data.get("location", ""),
        "numberOfFullTimeEmployees": parsed_data.get("numberOfFullTimeEmployees", ""),
        "building": parsed_data.get("building", ""),
        "county": {
            "street1": parsed_data.get("county", {}).get("street1", ""),
            "street2": parsed_data.get("county", {}).get("street2", ""),
            "city": parsed_data.get("county", {}).get("city", ""),
            "state": parsed_data.get("county", {}).get("state", ""),
            "zip": parsed_data.get("county", {}).get("zip", ""),
            "country": parsed_data.get("county", {}).get("country", "")
        },
        "location1": parsed_data.get("location1", ""),
        "partTimeEmployeesNumber": parsed_data.get("partTimeEmployeesNumber", 0),
        "building1": parsed_data.get("building1", ""),
        "annualRevenues": parsed_data.get("annualRevenues", 0),
        "location2": parsed_data.get("location2", ""),
        "building2": parsed_data.get("building2", ""),
        "location3": parsed_data.get("location3", ""),
        "building3": parsed_data.get("building3", ""),
        "descriptionOfPrimaryOperations": parsed_data.get("descriptionOfPrimaryOperations", ""),
        "agencyCustomerId2": parsed_data.get("agencyCustomerId2", ""),
        "priorCarrierForGeneralLiability": parsed_data.get("priorCarrierForGeneralLiability", ""),
        "priorCarrierForAutomobile": parsed_data.get("priorCarrierForAutomobile", ""),
        "priorCarrierForProperty": parsed_data.get("priorCarrierForProperty", ""),
        "agencyCustomerId3": parsed_data.get("agencyCustomerId3", ""),
        "producersName": parsed_data.get("producersName", ""),
        "depositAmount": parsed_data.get("depositAmount", ""),
        "minimumPremium": parsed_data.get("minimumPremium", ""),
        "policyPremium": parsed_data.get("policyPremium", ""),
        "hasEquipmentFloaterSectionsAttached": parsed_data.get("hasEquipmentFloaterSectionsAttached", False),
        "hasElectronicDataProcSectionAttached": parsed_data.get("hasElectronicDataProcSectionAttached", False),
        "hasAccountsReceivableAttached": parsed_data.get("hasAccountsReceivableAttached", False),
        "hasBoilerAndMachinery": parsed_data.get("hasBoilerAndMachinery", False),
        "hasBusinessAuto": parsed_data.get("hasBusinessAuto", False),
        "hasPropertySectionsAttached": parsed_data.get("hasPropertySectionsAttached", False),
        "hasTruckersMotorCarrierSectionsAttached": parsed_data.get("hasTruckersMotorCarrierSectionsAttached", False),
        "hasTransportationSectionsAttached": parsed_data.get("hasTransportationSectionsAttached", False),
        "policyNumber": parsed_data.get("policyNumber", ""),
        "agencyContactName": parsed_data.get("agencyContactName", ""),
        "agencyContactPhone": parsed_data.get("agencyContactPhone", ""),
        "agencyEmailAddress": parsed_data.get("agencyEmailAddress", ""),
        "proposedEffectiveDate": parsed_data.get("proposedEffectiveDate", ""),
        "billingPlanIsAgency": parsed_data.get("billingPlanIsAgency", False),
        "field16f996340b2011f083dfd3961689d753": parsed_data.get("field16f996340b2011f083dfd3961689d753", ""),
        "applicantIsNotForProfit": parsed_data.get("applicantIsNotForProfit", False),
        "applicantContactName": parsed_data.get("applicantContactName", ""),
        "applicantPhoneNumber": parsed_data.get("applicantPhoneNumber", ""),
        "applicantEmailAddress": parsed_data.get("applicantEmailAddress", ""),
        "premisesState": parsed_data.get("premisesState", ""),
        "hasFormalSafetyProgram": parsed_data.get("hasFormalSafetyProgram", ""),
        "followsOsha": parsed_data.get("followsOsha", ""),
        "hasSafetyPosition": parsed_data.get("hasSafetyPosition", ""),
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
    Uses Claude to intelligently interpret commands and update the form.
    """
    from logic.form_generation import update_form_logic
    
    # Use our intelligent form update logic
    updated_form = update_form_logic(current_form, command)
    
    return updated_form
