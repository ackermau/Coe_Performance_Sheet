from fastapi import FastAPI
from routes import rfq, machine, calculations

app = FastAPI()

# Include routers from different modules
app.include_router(rfq.router, prefix="/rfq", tags=["RFQ"])
app.include_router(machine.router, prefix="/machine", tags=["Machine"])
app.include_router(calculations.router, prefix="/calculate", tags=["Calculations"])

@app.get("/")
def home():
    return {"message": "RFQ System API is running"}
