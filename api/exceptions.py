from fastapi import HTTPException
import httpx

def handle_api_exception(e):
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    else:
        # For other exceptions, return default values
        return {
            "Company Name": "N/A",
            "Sector": "N/A",
            "Market Cap": "N/A",
            "P/E Ratio": "N/A",
            "Dividend Yield": "N/A",
            "Beta": "N/A",
            "Price to Book Ratio": "N/A",
            "Total Assets": 0,
            "Total Liabilities": 0,
            "Liquidity Ratio": 0.0,
            "Earnings Consistency": "N/A",
            "Debt to Equity Ratio": 0.0,
            "Earnings Growth Rate": 0.0,
            "Uninterrupted Dividends": False
        }


class CustomException(Exception):
    pass