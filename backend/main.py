from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api_interaction import fetch_company_financial_data, fetch_news_data, search_company_symbols
from exceptions import CustomException
import uvicorn

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",  # Allow requests from your local frontend
    "https://halal-stonks-ceu22mixz-intisharalams-projects.vercel.app",  # Add your Vercel frontend URL here
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Your existing FastAPI routes
class SymbolRequest(BaseModel):
    symbol: str

class SymbolSearchRequest(BaseModel):
    query: str

@app.get("/")
async def read_health():
    return {"status": "OK"}

@app.get("/multiply/")
async def multiply_numbers(x: int, y: int):
    return {"result": x * y}

@app.post("/api/search_symbols")
async def search_symbols(request: SymbolSearchRequest):
    query = request.query
    try:
        results = await search_company_symbols(query)
        return {"results": results}
    except CustomException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get_company_data")
async def get_company_data(request: SymbolRequest):
    symbol = request.symbol

    try:
        company_data = await fetch_company_financial_data(symbol)
    except CustomException as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Combine all data into a single response
    combined_data = {
        **company_data,
    }
    return {"message": "Company data fetched successfully", "data": combined_data}

@app.get("/api/get_newsfeed")
async def get_newsfeed():
    try:
        news_data = await fetch_news_data()
        return {"message": "News feed fetched successfully", "data": news_data}
    except CustomException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
