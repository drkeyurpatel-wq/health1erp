from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, patients, appointments, ipd, billing,
    inventory, pharmacy, laboratory, radiology, ot,
    reports, ai, audit, organizations,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(ipd.router, prefix="/ipd", tags=["IPD - Inpatient"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(pharmacy.router, prefix="/pharmacy", tags=["Pharmacy"])
api_router.include_router(laboratory.router, prefix="/laboratory", tags=["Laboratory"])
api_router.include_router(radiology.router, prefix="/radiology", tags=["Radiology"])
api_router.include_router(ot.router, prefix="/ot", tags=["Operation Theatre"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI & CDSS"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
