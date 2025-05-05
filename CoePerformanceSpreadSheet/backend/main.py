from fastapi import FastAPI
from routes import rfq, material_specs, tddbhd, reel_drive, str_utility
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

app.include_router(rfq.router, prefix="/api/rfq")
app.include_router(material_specs.router, prefix="/api/material_specs")
app.include_router(tddbhd.router, prefix="/api/tddbhd")
app.include_router(reel_drive.router, prefix="/api/reel_drive", tags=["Reel Drive"])
app.include_router(str_utility.router, prefix="/api/str_utility", tags=["Str Utility"])

@app.get("/")
def home():
    return {"message": "RFQ System API is running"}
