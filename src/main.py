"""
Main entry point for the FastAPI application.

"""

from fastapi import FastAPI
from routes import rfq, material_specs, tddbhd, reel_drive, str_utility
from routes.rolls import roll_str_backbend
from routes.feeds import sigma_five_feed, sigma_five_feed_with_pt, allen_bradley_mpl_feed
from routes.shears import single_rake_hyd_shear, bow_tie_hyd_shear
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}

# Allow requests from your TypeScript frontend
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4200",  # Angular dev server
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:5000",  # Flask dev server
    "http://localhost:8000",  # FastAPI dev server
    "http://127.0.0.1:5173",  # Vite dev server (alternative)
    "http://127.0.0.1:4200",  # Angular dev server (alternative)
    "http://127.0.0.1:3000",  # Next.js dev server (alternative)
    "http://127.0.0.1:5000",  # Flask dev server (alternative)
    "http://127.0.0.1:8000",  # FastAPI dev server (alternative)
    # Add your production domain when ready
    # "https://your-production-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.include_router(rfq.router, prefix="/rfq", tags=["RFQ"])
app.include_router(material_specs.router, prefix="/material_specs", tags=["Material Specs"])
app.include_router(tddbhd.router, prefix="/tddbhd", tags=["TDDBHD"])
app.include_router(reel_drive.router, prefix="/reel_drive", tags=["Reel Drive"])
app.include_router(str_utility.router, prefix="/str_utility", tags=["Str Utility"])
app.include_router(roll_str_backbend.router, prefix="/rolls/roll_str_backbend", tags=["Roll Str Backbend"])
app.include_router(sigma_five_feed.router, prefix="/feeds/sigma_five_feed", tags=["Feeds"])
app.include_router(sigma_five_feed_with_pt.router, prefix="/feeds/sigma_five_feed_with_pt", tags=["Feeds"])
app.include_router(allen_bradley_mpl_feed.router, prefix="/feeds/allen_bradley_mpl_feed", tags=["Feeds"])
app.include_router(single_rake_hyd_shear.router, prefix="/shears/single_rake_hyd_shear", tags=["Shears"])
app.include_router(bow_tie_hyd_shear.router, prefix="/shears/bow_tie_hyd_shear", tags=["Shears"])
