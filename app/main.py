from fastapi import FastAPI

app = FastAPI(
    title="Dental AI Receptionist",
    description="AI-powered receptionist for dental offices",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Dental AI Receptionist is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}