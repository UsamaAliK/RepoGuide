from fastapi import FastAPI,HTTPException
import requests



app=FastAPI()


# Endpoints
@app.get("/")
async def root():
    return {"message": "RepoGuide running"}