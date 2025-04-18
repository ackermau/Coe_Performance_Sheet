from fastapi import FastAPI
from routes import rfq, machine, material_specs, tddbhd
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
app.include_router(tddbhd.router, prefix="/api/tddbdhd")

# Include routers from different modules
app.include_router(rfq.router, prefix="/rfq", tags=["RFQ"])
app.include_router(machine.router, prefix="/machine", tags=["Machine"])
app.include_router(material_specs.router, prefix="/material_specs", tags=["Material Specs"])
app.include_router(tddbhd.router, prefix="/tddbhd", tags=["TDDBHD"])

@app.get("/")
def home():
    return {"message": "RFQ System API is running"}
