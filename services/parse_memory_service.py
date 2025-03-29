"""Service for parsing memory data using Claude's reasoning abilities.

Provides a function to extract key information using Claude to find relevant
fields for PDF form filling.
"""

import json
import os
from typing import Dict, Optional, Any
from anthropic import Anthropic
from services.clean_memory_service import clean_memory

def parse_memory_data(memory_data: Dict[str, Any], field_mapping: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
    """
    Uses Claude's reasoning capabilities to extract PDF form values from memory data.
    
    Args:
        memory_data: The raw memory data dictionary
        field_mapping: Dictionary mapping field names to descriptions of what to look for
                       If None, uses a default set of fields
    
    Returns:
        Properly structured data for PDF filling or None if required fields can't be found
    """
    # Set default field mapping if none provided
    if field_mapping is None:
        field_mapping = {
            "billingPlanForPolicyIsDirect": "The billing plan for the policy (e.g. Agency, Direct)",
            "applicantIsLLC": "The business entity type (e.g. Corporation, LLC, Partnership)",
            "dateOfApplication": "The date of application in YYYY-MM-DD format",
            "agency": "The agency name",
            "carrier": "The insurance carrier name",
            "naicCode": "The NAIC code",
            "companyPolicyOrProgramName": "The company policy or program name",
            "programCode": "The program code",
            "agencyCustomerId": "The agency customer ID",
            "hasBusinessOwnersAttachedSections": "Boolean indicating if business owners sections are attached",
            "hasCommercialGeneralLiabilitySectionsAttached": "Boolean indicating if commercial general liability sections are attached",
            "paymentPlan": "The payment plan",
            "methodOfPayment": "The method of payment",
            "audit1": "Audit information",
            "applicantName1.firstName": "The first name of the main contact or applicant",
            "applicantName1.mi": "The middle initial of the main contact or applicant",
            "applicantName1.lastName": "The last name of the main contact or applicant", 
            "glCode1": "The GL code",
            "sic1": "The SIC code",
            "naics1": "The NAICS code",
            "feinOrSocSec1": "The FEIN or SSN",
            "websiteAddress.street1": "Street address line 1 for the website address",
            "websiteAddress.street2": "Street address line 2 for the website address",
            "websiteAddress.city": "City for the website address",
            "websiteAddress.state": "State for the website address",
            "websiteAddress.zip": "ZIP code for the website address",
            "websiteAddress.country": "Country for the website address",
            "contactInformationPrimary1": "The primary contact information type",
            "contactInformationSecondary1": "The secondary contact information type",
            "premisesZipcode.street1": "Street address line 1 for the premises",
            "premisesZipcode.street2": "Street address line 2 for the premises",
            "premisesZipcode.city": "City for the premises",
            "premisesZipcode.state": "State for the premises",
            "premisesZipcode.zip": "ZIP code for the premises",
            "premisesZipcode.country": "Country for the premises",
            "agencyCustomerId1": "The agency customer ID (secondary)",
            "location": "The location number",
            "numberOfFullTimeEmployees": "The number of full-time employees",
            "building": "The building number",
            "county.street1": "Street address line 1 for the county",
            "county.street2": "Street address line 2 for the county",
            "county.city": "City for the county",
            "county.state": "State for the county",
            "county.zip": "ZIP code for the county",
            "county.country": "Country for the county",
            "location1": "The location number (secondary)",
            "partTimeEmployeesNumber": "The number of part-time employees",
            "building1": "The building number (secondary)",
            "annualRevenues": "The annual revenues",
            "location2": "The location number (tertiary)",
            "building2": "The building number (tertiary)",
            "location3": "The location number (quaternary)",
            "building3": "The building number (quaternary)",
            "descriptionOfPrimaryOperations": "Description of primary operations",
            "agencyCustomerId2": "The agency customer ID (tertiary)",
            "priorCarrierForGeneralLiability": "The prior carrier for general liability",
            "priorCarrierForAutomobile": "The prior carrier for automobile",
            "priorCarrierForProperty": "The prior carrier for property",
            "agencyCustomerId3": "The agency customer ID (quaternary)",
            "producersName": "The producer's name",
            "depositAmount": "The deposit amount",
            "minimumPremium": "The minimum premium",
            "policyPremium": "The policy premium",
            "hasEquipmentFloaterSectionsAttached": "Boolean indicating if equipment floater sections are attached",
            "hasElectronicDataProcSectionAttached": "Boolean indicating if electronic data processing sections are attached",
            "hasAccountsReceivableAttached": "Boolean indicating if accounts receivable sections are attached",
            "hasBoilerAndMachinery": "Boolean indicating if boiler and machinery sections are attached",
            "hasBusinessAuto": "Boolean indicating if business auto sections are attached",
            "hasPropertySectionsAttached": "Boolean indicating if property sections are attached",
            "hasTruckersMotorCarrierSectionsAttached": "Boolean indicating if truckers motor carrier sections are attached",
            "hasTransportationSectionsAttached": "Boolean indicating if transportation sections are attached",
            "policyNumber": "The policy number",
            "agencyContactName": "The agency contact name",
            "agencyContactPhone": "The agency contact phone",
            "agencyEmailAddress": "The agency email address",
            "proposedEffectiveDate": "The proposed effective date",
            "billingPlanIsAgency": "Boolean indicating if billing plan is agency",
            "field16f996340b2011f083dfd3961689d753": "Direct field",
            "applicantIsNotForProfit": "Boolean indicating if applicant is not for profit",
            "applicantContactName": "The applicant contact name",
            "applicantPhoneNumber": "The applicant phone number",
            "applicantEmailAddress": "The applicant email address",
            "premisesState": "The premises state",
            "hasFormalSafetyProgram": "Boolean indicating if there is a formal safety program",
            "followsOsha": "Boolean indicating if OSHA guidelines are followed",
            "hasSafetyPosition": "Boolean indicating if there is a safety position"
        }
    
    # Clean the memory data first
    cleaned_data = clean_memory(memory_data)
    
    # Convert to JSON string for Claude API with proper escaping
    data_json = json.dumps(cleaned_data)
    
    # Construct the field descriptions for the prompt
    field_descriptions = []
    for i, (key, description) in enumerate(field_mapping.items()):
        field_descriptions.append(f"{i+1}. {key} - {description}")
    
    field_description_text = "\n".join(field_descriptions)
    
    # Build the expected output structure based on the field mapping
    output_structure = {}
    nested_fields = {}
    
    # Group nested fields
    for key in field_mapping:
        if "." in key:
            parent, child = key.split(".", 1)
            if parent not in nested_fields:
                nested_fields[parent] = []
            nested_fields[parent].append(child)
        else:
            output_structure[key] = "string or null"
    
    # Add nested structures
    for parent, children in nested_fields.items():
        child_dict = {child: "string or null" for child in children}
        output_structure[parent] = child_dict
    
    # Convert to JSON string for the prompt
    output_example = json.dumps(output_structure, indent=4)
    
    # Define the prompt for Claude
    prompt = f"""
    You are an expert at extracting relevant information from JSON data. 
    I have customer data in JSON format, and I need to extract specific fields for a PDF form.
    
    Here's the JSON data:
    ```json
    {data_json}
    ```
    
    I need you to find these values:
    {field_description_text}
    
    Some important notes:
    - Only extract values that actually exist in the data - don't make anything up
    - If you can't find a value, use null
    - You need to reason about which fields make the most sense to use
    - The data structure might be different from case to case
    - Sometimes the data might be nested under company.json.company, other times elsewhere
    
    Your response should be ONLY a JSON object with this structure:
    {output_example}
    """
    
    # Get Anthropic API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)
    
    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            system="You are an expert at extracting relevant information from JSON data for PDF form filling. You should only return valid JSON that matches the requested structure exactly."
        )
        
        content = message.content[0].text
        
        # Extract the JSON part
        if "```json" in content:
            json_content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_content = content.split("```")[1].strip()
        else:
            json_content = content.strip()
        
        # Parse the extracted JSON
        result = json.loads(json_content)
        
        # Validate the structure matches our expected output
        for key in output_structure:
            if key not in result:
                print(f"Missing expected key: {key}")
                return None
            
            if isinstance(output_structure[key], dict):
                if not isinstance(result[key], dict):
                    print(f"Expected {key} to be a dictionary")
                    return None
                
                for child_key in output_structure[key]:
                    if child_key not in result[key]:
                        print(f"Missing expected key: {key}.{child_key}")
                        return None
        
        return result
    
    except Exception as e:
        print(f"Error with Claude API: {str(e)}")
        return None