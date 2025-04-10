from fastapi import APIRouter

from wellfix_api.api.v1.endpoints import (
    auth, users, admin_users, profiles, addresses, 
    service_areas, admin_service_areas, jobs, ratings, admin_reports, pricing, admin_pricing
)

api_router = APIRouter()

# Include all endpoint modules with their prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["Admin: Users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
api_router.include_router(service_areas.router, prefix="/service-areas", tags=["Service Areas"])
api_router.include_router(admin_service_areas.router, prefix="/admin/serviceable-areas", tags=["Admin: Service Areas"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(ratings.router, tags=["Ratings"])
api_router.include_router(admin_reports.router, prefix="/admin/reports", tags=["Admin: Reports"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
api_router.include_router(admin_pricing.router, prefix="/admin/pricing", tags=["Admin: Pricing Config"])
