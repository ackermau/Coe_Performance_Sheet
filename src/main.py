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

# Allow requests from your frontend (React app)
origins = [
    "http://localhost:3000",  # React dev server
    # "http://your-prod-domain.com"  <-- add this later for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allows listed domains
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # allow all headers
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
