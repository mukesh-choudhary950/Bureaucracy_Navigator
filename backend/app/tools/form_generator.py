from typing import Dict, Any, List
from app.tools.base import BaseTool, ToolResult
import json
from datetime import datetime

class FormGeneratorTool(BaseTool):
    name = "form_generator"
    description = "Generate pre-filled forms for government applications"
    
    async def execute(self, form_type: str, user_data: Dict[str, Any]) -> ToolResult:
        """Generate a pre-filled form based on user data"""
        try:
            # Form templates for different government applications
            form_templates = {
                "income_certificate": self._generate_income_certificate_form,
                "driving_license": self._generate_driving_license_form,
                "caste_certificate": self._generate_caste_certificate_form,
                "birth_certificate": self._generate_birth_certificate_form
            }
            
            if form_type not in form_templates:
                return ToolResult(
                    success=False,
                    error=f"Unsupported form type: {form_type}"
                )
            
            form_data = form_templates[form_type](user_data)
            
            return ToolResult(
                success=True,
                data={
                    "form_type": form_type,
                    "form_data": form_data,
                    "generated_at": datetime.now().isoformat(),
                    "instructions": self._get_form_instructions(form_type)
                },
                metadata={"template_version": "1.0"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Form generation error: {str(e)}"
            )
    
    def _generate_income_certificate_form(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate income certificate form data"""
        return {
            "application_details": {
                "form_name": "Income Certificate Application",
                "state": user_data.get("state", "Telangana"),
                "district": user_data.get("district", ""),
                "mandal": user_data.get("mandal", ""),
                "village": user_data.get("village", "")
            },
            "applicant_details": {
                "name": user_data.get("name", ""),
                "father_name": user_data.get("father_name", ""),
                "mother_name": user_data.get("mother_name", ""),
                "age": user_data.get("age", ""),
                "gender": user_data.get("gender", ""),
                "aadhaar": user_data.get("aadhaar", ""),
                "mobile": user_data.get("mobile", ""),
                "email": user_data.get("email", "")
            },
            "address_details": {
                "house_number": user_data.get("house_number", ""),
                "street": user_data.get("street", ""),
                "area": user_data.get("area", ""),
                "city": user_data.get("city", ""),
                "pincode": user_data.get("pincode", ""),
                "district": user_data.get("district", ""),
                "state": user_data.get("state", "Telangana")
            },
            "income_details": {
                "annual_income": user_data.get("annual_income", ""),
                "income_source": user_data.get("income_source", ""),
                "occupation": user_data.get("occupation", ""),
                "employer_name": user_data.get("employer_name", ""),
                "employer_address": user_data.get("employer_address", "")
            },
            "required_documents": [
                "Aadhaar Card",
                "Voter ID / Ration Card",
                "Income Proof (Salary Certificate/IT Returns)",
                "Address Proof",
                "Passport Size Photographs (2)",
                "Self-Declaration Form"
            ]
        }
    
    def _generate_driving_license_form(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate driving license form data"""
        return {
            "application_details": {
                "form_name": "Driving License Application",
                "license_type": user_data.get("license_type", "Private Motor Vehicle"),
                "rto_office": user_data.get("rto_office", "")
            },
            "applicant_details": {
                "name": user_data.get("name", ""),
                "father_name": user_data.get("father_name", ""),
                "date_of_birth": user_data.get("date_of_birth", ""),
                "gender": user_data.get("gender", ""),
                "blood_group": user_data.get("blood_group", ""),
                "qualification": user_data.get("qualification", ""),
                "aadhaar": user_data.get("aadhaar", ""),
                "mobile": user_data.get("mobile", ""),
                "email": user_data.get("email", "")
            },
            "address_details": {
                "permanent_address": user_data.get("permanent_address", {}),
                "temporary_address": user_data.get("temporary_address", {})
            },
            "vehicle_details": {
                "vehicle_type": user_data.get("vehicle_type", ""),
                "vehicle_class": user_data.get("vehicle_class", ""),
                "vehicle_registration": user_data.get("vehicle_registration", "")
            },
            "required_documents": [
                "Aadhaar Card",
                "Proof of Address",
                "Proof of Date of Birth",
                "Passport Size Photographs (3)",
                "Learner's License (if applicable)",
                "Medical Certificate (for commercial license)"
            ]
        }
    
    def _generate_caste_certificate_form(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate caste certificate form data"""
        return {
            "application_details": {
                "form_name": "Caste Certificate Application",
                "state": user_data.get("state", "Telangana"),
                "district": user_data.get("district", ""),
                "caste_category": user_data.get("caste_category", "")
            },
            "applicant_details": {
                "name": user_data.get("name", ""),
                "father_name": user_data.get("father_name", ""),
                "mother_name": user_data.get("mother_name", ""),
                "age": user_data.get("age", ""),
                "gender": user_data.get("gender", ""),
                "aadhaar": user_data.get("aadhaar", ""),
                "mobile": user_data.get("mobile", "")
            },
            "caste_details": {
                "caste": user_data.get("caste", ""),
                "sub_caste": user_data.get("sub_caste", ""),
                "religion": user_data.get("religion", ""),
                "mother_tongue": user_data.get("mother_tongue", "")
            },
            "address_details": {
                "house_number": user_data.get("house_number", ""),
                "street": user_data.get("street", ""),
                "village": user_data.get("village", ""),
                "mandal": user_data.get("mandal", ""),
                "district": user_data.get("district", ""),
                "pincode": user_data.get("pincode", "")
            },
            "required_documents": [
                "Aadhaar Card",
                "Voter ID / Ration Card",
                "Birth Certificate",
                "Caste Certificate of Parent/Guardian",
                "Address Proof",
                "Passport Size Photographs (2)",
                "Self-Declaration Form"
            ]
        }
    
    def _generate_birth_certificate_form(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate birth certificate form data"""
        return {
            "application_details": {
                "form_name": "Birth Certificate Application",
                "hospital_name": user_data.get("hospital_name", ""),
                "place_of_birth": user_data.get("place_of_birth", "")
            },
            "child_details": {
                "name": user_data.get("child_name", ""),
                "date_of_birth": user_data.get("date_of_birth", ""),
                "time_of_birth": user_data.get("time_of_birth", ""),
                "gender": user_data.get("gender", ""),
                "birth_weight": user_data.get("birth_weight", ""),
                "place_of_birth": user_data.get("place_of_birth", "")
            },
            "parent_details": {
                "father_name": user_data.get("father_name", ""),
                "father_age": user_data.get("father_age", ""),
                "father_occupation": user_data.get("father_occupation", ""),
                "father_aadhaar": user_data.get("father_aadhaar", ""),
                "mother_name": user_data.get("mother_name", ""),
                "mother_age": user_data.get("mother_age", ""),
                "mother_occupation": user_data.get("mother_occupation", ""),
                "mother_aadhaar": user_data.get("mother_aadhaar", "")
            },
            "address_details": {
                "house_number": user_data.get("house_number", ""),
                "street": user_data.get("street", ""),
                "area": user_data.get("area", ""),
                "city": user_data.get("city", ""),
                "district": user_data.get("district", ""),
                "pincode": user_data.get("pincode", "")
            },
            "required_documents": [
                "Hospital Discharge Certificate",
                "Parents' Aadhaar Cards",
                "Parents' Marriage Certificate",
                "Address Proof",
                "Birth Registration Form from Hospital",
                "Affidavit (if delayed registration)"
            ]
        }
    
    def _get_form_instructions(self, form_type: str) -> List[str]:
        """Get instructions for filling the form"""
        instructions = {
            "income_certificate": [
                "Fill in all mandatory fields marked with *",
                "Attach self-attested copies of all required documents",
                "Sign the application form",
                "Submit to the nearest MeeSeva center",
                "Pay the prescribed fee (usually ₹35)",
                "Certificate will be issued within 7 working days"
            ],
            "driving_license": [
                "Fill the application form online or offline",
                "Attach required documents",
                "Visit the RTO office for verification",
                "Pass the driving test",
                "Pay the license fee",
                "License will be issued after successful test"
            ],
            "caste_certificate": [
                "Fill in complete caste details",
                "Attach parent's caste certificate",
                "Get verification from village/taluk officer",
                "Submit to revenue department",
                "Certificate will be issued after verification (15-30 days)"
            ],
            "birth_certificate": [
                "Apply within 21 days of birth (no fee)",
                "After 21 days but within 30 days (late fee ₹2)",
                "After 30 days but within 1 year (late fee ₹5)",
                "After 1 year (requires court order)",
                "Submit to municipal corporation or panchayat office"
            ]
        }
        
        return instructions.get(form_type, ["Follow the instructions on the form"])
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "form_type": {
                    "type": "string",
                    "enum": ["income_certificate", "driving_license", "caste_certificate", "birth_certificate"],
                    "description": "Type of form to generate"
                },
                "user_data": {
                    "type": "object",
                    "description": "User data to pre-fill the form",
                    "properties": {
                        "name": {"type": "string"},
                        "father_name": {"type": "string"},
                        "mother_name": {"type": "string"},
                        "age": {"type": "string"},
                        "gender": {"type": "string"},
                        "aadhaar": {"type": "string"},
                        "mobile": {"type": "string"},
                        "email": {"type": "string"},
                        "address": {"type": "object"},
                        "district": {"type": "string"},
                        "state": {"type": "string", "default": "Telangana"}
                    }
                }
            },
            "required": ["form_type", "user_data"]
        }
