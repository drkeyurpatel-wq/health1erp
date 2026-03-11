"""HL7 v2 and FHIR R4 interoperability utilities."""
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


def parse_hl7_message(raw_message: str) -> dict:
    """Parse an HL7 v2.x message into a structured dict."""
    segments = {}
    for line in raw_message.strip().split("\r"):
        if not line:
            continue
        fields = line.split("|")
        seg_type = fields[0]
        segments[seg_type] = fields[1:]
    return segments


def create_hl7_adt(
    event_type: str, patient_data: dict, admission_data: Optional[dict] = None
) -> str:
    """Create an HL7 ADT (Admit/Discharge/Transfer) message."""
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    pid = patient_data

    msg = f"MSH|^~\\&|HEALTH1ERP|HOSPITAL|RECEIVER|DEST|{now}||ADT^{event_type}|{now}|P|2.5\r"
    msg += f"EVN|{event_type}|{now}\r"
    msg += f"PID|1||{pid.get('uhid', '')}||{pid.get('last_name', '')}^{pid.get('first_name', '')}||{pid.get('dob', '')}|{pid.get('gender', 'U')}|||{pid.get('address', '')}||{pid.get('phone', '')}\r"

    if admission_data:
        msg += f"PV1|1|I|{admission_data.get('ward', '')}^{admission_data.get('bed', '')}|||{admission_data.get('doctor', '')}|||||||||||{admission_data.get('admission_type', '')}\r"

    return msg


def patient_to_fhir(patient_data: dict) -> dict:
    """Convert a patient record to FHIR R4 Patient resource."""
    return {
        "resourceType": "Patient",
        "id": str(patient_data.get("id", "")),
        "identifier": [
            {"system": "urn:health1erp:uhid", "value": patient_data.get("uhid", "")},
        ],
        "name": [
            {
                "family": patient_data.get("last_name", ""),
                "given": [patient_data.get("first_name", "")],
                "use": "official",
            }
        ],
        "gender": _fhir_gender(patient_data.get("gender", "")),
        "birthDate": str(patient_data.get("date_of_birth", "")),
        "telecom": [
            {"system": "phone", "value": patient_data.get("phone", ""), "use": "mobile"},
        ],
        "address": [_fhir_address(patient_data.get("address", {}))],
    }


def admission_to_fhir(admission_data: dict, patient_id: str) -> dict:
    """Convert an admission to FHIR R4 Encounter resource."""
    status_map = {
        "Admitted": "in-progress",
        "Discharged": "finished",
        "Transferred": "in-progress",
        "LAMA": "finished",
        "Expired": "finished",
    }
    return {
        "resourceType": "Encounter",
        "id": str(admission_data.get("id", "")),
        "status": status_map.get(admission_data.get("status", ""), "unknown"),
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "IMP",
            "display": "inpatient encounter",
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "period": {
            "start": str(admission_data.get("admission_date", "")),
            "end": str(admission_data.get("discharge_date", "")) if admission_data.get("discharge_date") else None,
        },
        "reasonCode": [
            {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10", "code": code}]}
            for code in admission_data.get("icd_codes", [])
        ],
    }


def lab_result_to_fhir(result_data: dict, patient_id: str) -> dict:
    """Convert a lab result to FHIR R4 Observation resource."""
    return {
        "resourceType": "Observation",
        "id": str(result_data.get("id", "")),
        "status": "final" if result_data.get("verified_at") else "preliminary",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}],
        "code": {"text": result_data.get("test_name", "")},
        "subject": {"reference": f"Patient/{patient_id}"},
        "valueString": result_data.get("result_value", ""),
        "interpretation": [{"coding": [{"code": "A" if result_data.get("is_abnormal") else "N"}]}],
    }


def _fhir_gender(gender: str) -> str:
    mapping = {"Male": "male", "Female": "female", "Other": "other"}
    return mapping.get(gender, "unknown")


def _fhir_address(address: dict) -> dict:
    return {
        "line": [address.get("street", "")],
        "city": address.get("city", ""),
        "state": address.get("state", ""),
        "postalCode": address.get("zip", ""),
        "country": address.get("country", "IN"),
    }
