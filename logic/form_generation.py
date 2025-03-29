"""
Business/domain logic for form generation and updating.
"""
from services.anvil_api import fill_pdf_with_anvil
from services.clean_memory_service import clean_memory
from services.parse_memory_service import parse_memory_data
import os
from typing import Dict, Any
from config import ANVIL_TEMPLATE_EID

def generate_form(company_id: int, memory_data: Dict[str, Any]) -> str:
    """
    1) Use the provided memory data to fill out an initial PDF form with Anvil
    2) Save the PDF and return a URL path to it
    """
    # Clean and extract all fields from memory data using Claude
    # Note: parse_memory_data already calls clean_memory internally
    parsed_data = parse_memory_data(memory_data)
    
    # Prepare data structure for Anvil
    data_for_anvil = {
        "title": "Acord 125",
        "fontSize": 10,
        "textColor": "#333333",
        "data": {
            "billingPlanForPolicyIsDirect": parsed_data.get("billingPlanForPolicyIsDirect"),
            "applicantIsLLC": parsed_data.get("applicantIsLLC"),
            "dateOfApplication": parsed_data.get("dateOfApplication"),
            "agency": parsed_data.get("agency"),
            "carrier": parsed_data.get("carrier"),
            "naicCode": parsed_data.get("naicCode"),
            "companyPolicyOrProgramName": parsed_data.get("companyPolicyOrProgramName"),
            "programCode": parsed_data.get("programCode"),
            "agencyCustomerId": parsed_data.get("agencyCustomerId"),
            "hasBusinessOwnersAttachedSections": parsed_data.get("hasBusinessOwnersAttachedSections"),
            "hasCommercialGeneralLiabilitySectionsAttached": parsed_data.get("hasCommercialGeneralLiabilitySectionsAttached"),
            "paymentPlan": parsed_data.get("paymentPlan"),
            "methodOfPayment": parsed_data.get("methodOfPayment"),
            "audit1": parsed_data.get("audit1"),
            "applicantName1": {
                "firstName": parsed_data.get("applicantName1", {}).get("firstName"),
                "mi": parsed_data.get("applicantName1", {}).get("mi"),
                "lastName": parsed_data.get("applicantName1", {}).get("lastName")
            },
            "glCode1": parsed_data.get("glCode1"),
            "sic1": parsed_data.get("sic1"),
            "naics1": parsed_data.get("naics1"),
            "feinOrSocSec1": parsed_data.get("feinOrSocSec1"),
            "websiteAddress": {
                "street1": parsed_data.get("websiteAddress", {}).get("street1"),
                "street2": parsed_data.get("websiteAddress", {}).get("street2"),
                "city": parsed_data.get("websiteAddress", {}).get("city"),
                "state": parsed_data.get("websiteAddress", {}).get("state"),
                "zip": parsed_data.get("websiteAddress", {}).get("zip"),
                "country": parsed_data.get("websiteAddress", {}).get("country")
            },
            "contactInformationPrimary1": parsed_data.get("contactInformationPrimary1"),
            "contactInformationSecondary1": parsed_data.get("contactInformationSecondary1"),
            "premisesZipcode": {
                "street1": parsed_data.get("premisesZipcode", {}).get("street1"),
                "street2": parsed_data.get("premisesZipcode", {}).get("street2"),
                "city": parsed_data.get("premisesZipcode", {}).get("city"),
                "state": parsed_data.get("premisesZipcode", {}).get("state"),
                "zip": parsed_data.get("premisesZipcode", {}).get("zip"),
                "country": parsed_data.get("premisesZipcode", {}).get("country")
            },
            "agencyCustomerId1": parsed_data.get("agencyCustomerId1"),
            "location": parsed_data.get("location"),
            "numberOfFullTimeEmployees": parsed_data.get("numberOfFullTimeEmployees"),
            "building": parsed_data.get("building"),
            "county": {
                "street1": parsed_data.get("county", {}).get("street1"),
                "street2": parsed_data.get("county", {}).get("street2"),
                "city": parsed_data.get("county", {}).get("city"),
                "state": parsed_data.get("county", {}).get("state"),
                "zip": parsed_data.get("county", {}).get("zip"),
                "country": parsed_data.get("county", {}).get("country")
            },
            "location1": parsed_data.get("location1"),
            "partTimeEmployeesNumber": parsed_data.get("partTimeEmployeesNumber"),
            "building1": parsed_data.get("building1"),
            "annualRevenues": parsed_data.get("annualRevenues"),
            "location2": parsed_data.get("location2"),
            "building2": parsed_data.get("building2"),
            "location3": parsed_data.get("location3"),
            "building3": parsed_data.get("building3"),
            "descriptionOfPrimaryOperations": parsed_data.get("descriptionOfPrimaryOperations"),
            "agencyCustomerId2": parsed_data.get("agencyCustomerId2"),
            "priorCarrierForGeneralLiability": parsed_data.get("priorCarrierForGeneralLiability"),
            "priorCarrierForAutomobile": parsed_data.get("priorCarrierForAutomobile"),
            "priorCarrierForProperty": parsed_data.get("priorCarrierForProperty"),
            "agencyCustomerId3": parsed_data.get("agencyCustomerId3"),
            "producersName": parsed_data.get("producersName"),
            "depositAmount": parsed_data.get("depositAmount"),
            "minimumPremium": parsed_data.get("minimumPremium"),
            "policyPremium": parsed_data.get("policyPremium"),
            "hasEquipmentFloaterSectionsAttached": parsed_data.get("hasEquipmentFloaterSectionsAttached"),
            "hasElectronicDataProcSectionAttached": parsed_data.get("hasElectronicDataProcSectionAttached"),
            "hasAccountsReceivableAttached": parsed_data.get("hasAccountsReceivableAttached"),
            "hasBoilerAndMachinery": parsed_data.get("hasBoilerAndMachinery"),
            "hasBusinessAuto": parsed_data.get("hasBusinessAuto"),
            "hasPropertySectionsAttached": parsed_data.get("hasPropertySectionsAttached"),
            "hasTruckersMotorCarrierSectionsAttached": parsed_data.get("hasTruckersMotorCarrierSectionsAttached"),
            "hasTransportationSectionsAttached": parsed_data.get("hasTransportationSectionsAttached"),
            "policyNumber": parsed_data.get("policyNumber"),
            "agencyContactName": parsed_data.get("agencyContactName"),
            "agencyContactPhone": parsed_data.get("agencyContactPhone"),
            "agencyEmailAddress": parsed_data.get("agencyEmailAddress"),
            "proposedEffectiveDate": parsed_data.get("proposedEffectiveDate"),
            "billingPlanIsAgency": parsed_data.get("billingPlanIsAgency"),
            "field16f996340b2011f083dfd3961689d753": parsed_data.get("field16f996340b2011f083dfd3961689d753"),
            "applicantIsNotForProfit": parsed_data.get("applicantIsNotForProfit"),
            "applicantContactName": parsed_data.get("applicantContactName"),
            "applicantPhoneNumber": parsed_data.get("applicantPhoneNumber"),
            "applicantEmailAddress": parsed_data.get("applicantEmailAddress"),
            "premisesState": parsed_data.get("premisesState"),
            "hasFormalSafetyProgram": parsed_data.get("hasFormalSafetyProgram"),
            "followsOsha": parsed_data.get("followsOsha"),
            "hasSafetyPosition": parsed_data.get("hasSafetyPosition")
        }
    }

    # Get PDF bytes from Anvil
    pdf_bytes = fill_pdf_with_anvil(data_for_anvil)
    
    # Create a unique filename for this company's form
    filename = f"form_{company_id}.pdf"
    filepath = os.path.join("static", "forms", filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save the PDF
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    
    # Return the URL path to the saved PDF
    return f"/static/forms/{filename}"

def update_form_logic(form_data, update_command: str):
    """
    Naive text-based update. Expand with LLM or parsing if needed.
    """
    if "deductible" in update_command.lower():
        form_data["deductible"] = "$5000"
    return form_data
