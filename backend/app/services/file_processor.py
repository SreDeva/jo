import requests
import os
import json
import uuid
from typing import List, Dict, Any
from fastapi import HTTPException

# OpenRouter API credentials
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_api_key_here")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def extract_vendors_from_document(file_content: bytes, file_name: str) -> List[Dict[str, Any]]:
    """
    Extract vendor information from uploaded distributor document using OpenRouter API
    
    Args:
        file_content: Raw file content as bytes
        file_name: Name of the uploaded file
        
    Returns:
        List of vendor dictionaries with name and email
    """
    try:
        # Decode file content to text
        text_data = file_content.decode("utf-8", errors="ignore")
        
        # Build payload for OpenRouter API
        payload = {
            "model": "x-ai/grok-4-fast:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict JSON generator that extracts vendor information "
                        "from distributor documents. Use this exact schema:\n\n"
                        "{\n"
                        "  \"vendors\": [\n"
                        "    {\n"
                        "      \"name\": \"string\",\n"
                        "      \"email\": \"string\"\n"
                        "    }\n"
                        "  ]\n"
                        "}\n\n"
                        "CRITICAL RULES:\n"
                        "- Return only valid JSON (no markdown, no code blocks).\n"
                        "- Extract vendor/company names and their corresponding email addresses.\n"
                        "- Look for email patterns: text@domain.com, contact@company.com, etc.\n"
                        "- Match emails with their associated vendor/company names in the document.\n"
                        "- Email addresses typically appear near company names, in contact sections, or signature blocks.\n"
                        "- Common email patterns: info@, contact@, sales@, support@, admin@ followed by company domain.\n"
                        "- If you find a company name but no email, use empty string for email field.\n"
                        "- Do not invent email addresses - only extract what's clearly present.\n"
                        "- Look for patterns like 'Company Name: email@domain.com' or 'Contact: name@company.com'.\n"
                        "- Each vendor must have exactly these two fields: name and email."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Extract all vendor/company names and their email addresses from this distributor file ({file_name}). Look carefully for email patterns (anything@domain.com) and match them with company names. If a company has multiple emails, pick the primary contact email:\n\n{text_data}"
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Call OpenRouter API
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"OpenRouter API error: {response.status_code}")
            
        data = response.json()
        
        # Extract JSON from LLM response
        extracted_content = data["choices"][0]["message"]["content"]
        
        # Clean up the response (remove any markdown formatting)
        if extracted_content.startswith("```json"):
            extracted_content = extracted_content.replace("```json", "").replace("```", "").strip()
        elif extracted_content.startswith("```"):
            extracted_content = extracted_content.replace("```", "").strip()
            
        # Parse the JSON
        try:
            vendor_data = json.loads(extracted_content)
            vendors = vendor_data.get("vendors", [])
            
            # Validate and clean vendor data
            processed_vendors = []
            for vendor in vendors:
                if isinstance(vendor, dict) and vendor.get("name"):
                    processed_vendor = {
                        "name": vendor.get("name", "").strip(),
                        "email": vendor.get("email", "").strip(),
                        "vendor_id": str(uuid.uuid4())[:24]  # Generate unique vendor_id
                    }
                    processed_vendors.append(processed_vendor)
            
            return processed_vendors
            
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse vendor data: {str(e)}")
            
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Unable to read file content. Please ensure the file is a valid text document.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

def validate_extracted_vendors(vendors: List[Dict[str, Any]]) -> bool:
    """
    Validate that extracted vendor data has the required structure
    
    Args:
        vendors: List of vendor dictionaries
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not isinstance(vendors, list):
        raise HTTPException(status_code=400, detail="Invalid vendor data format")
    
    if len(vendors) == 0:
        raise HTTPException(status_code=400, detail="No vendors found in the document")
    
    for vendor in vendors:
        if not isinstance(vendor, dict):
            raise HTTPException(status_code=400, detail="Invalid vendor data structure")
        
        if not vendor.get("name"):
            raise HTTPException(status_code=400, detail="Vendor name is required for all vendors")
    
    return True