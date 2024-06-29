import httpx
import os
import yfinance as yf
from exceptions import handle_api_exception, CustomException
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables from .env file
load_dotenv()

STOCK_API_KEY = os.getenv('NEXT_PUBLIC_STOCK_API_KEY')
#print(STOCK_API_KEY)

NEWS_API_KEY = os.getenv('NEXT_PUBLIC_NEWS_API_KEY')


async def fetch_news_data():
    try:
        url = f'https://api.currentsapi.services/v1/latest-news'
        params = {
            'apiKey': NEWS_API_KEY,
            'language': 'en',  # Optional: Specify language (e.g., 'en' for English)
            'category': 'finance',  # Optional: Specify a category (e.g., 'finance', 'business', etc.)
            'q': 'stock market',  # Optional: Search query keywords
            'pageSize': 10,  # Limit to 10 articles (maximum is 100)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            news_data = response.json().get('news', [])
            #print(news_data)
            return news_data
    except httpx.HTTPStatusError as e:
        raise CustomException(f"Error fetching news: {str(e)}")
    except Exception as e:
        raise CustomException(f"Unexpected error fetching news: {str(e)}")


#"""
async def search_company_symbols(query):
    url = f"https://financialmodelingprep.com/api/v3/search?query={query}&apikey={STOCK_API_KEY}"
    print(f"Search URL: {url}\n")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        if data:
            results = [{"name": f"{item['name']} ({item['symbol']})", "symbol": item['symbol']} for item in data]
            return results
        else:
            return []
    except httpx.HTTPStatusError as e:
        raise CustomException(f"HTTP error occurred: {str(e)}")
    except Exception as e:
        raise CustomException(f"An error occurred: {str(e)}")


async def fetch_company_financial_data(symbol):
    try:
        stock = yf.Ticker(symbol)

        profile_data = stock.info
        profile_data = clean_profile_data(profile_data)
        #print(profile_data)

        historical_price = stock.history(period='2y', interval='1wk')
        historical_price = historical_price.to_dict('index')
        historical_price = [{'time': date.strftime('%Y/%m/%d'), 'price': round(info['Close'], 2)} for date, info in historical_price.items()]
        #print(historical_price)
        
        financials = stock.financials

        netIncome = financials.loc['Net Income']
        netIncome = netIncome.dropna()
        
        start_income = netIncome.iloc[-1]
        latest_income = netIncome.iloc[0]
        growthRate = (latest_income - start_income) /(start_income) * 100
        growthRate = round(growthRate, 2)
        


        dividends = stock.dividends
        if len(dividends) >= 10:
            dividends = dividends.tail(10)
        else:
            dividends = dividends.tail(len(dividends))
        df = pd.DataFrame(dividends)
        Interrupted_Dividends = (df['Dividends'] <= 0).any()
        print( not Interrupted_Dividends)



        # Fetch balance sheet data
        balance_sheet = stock.balance_sheet

        # Check if 'Total Liabilities' or similar exists
        if 'Total Liabilities' in balance_sheet.index:
            total_liabilities = balance_sheet.loc['Total Liabilities']
        elif 'Total Liabilities Net Minority Interest' in balance_sheet.index:
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest']
        else:
            raise KeyError("Total Liabilities not found in the balance sheet data.")

        # Get total assets
        total_assets = balance_sheet.loc['Total Assets']

        # Get the top 3 most recent values
        top_3_assets = total_assets.head(3)
        top_3_liabilities = total_liabilities.head(3)

        # Combine into the desired format
        Assets_Liabilities = []
        for year in top_3_assets.index:
            Assets_Liabilities.append({
                'year': year.strftime('%Y'),  # Only the year part
                'assets': top_3_assets[year],
                'liabilities': top_3_liabilities[year]
            })

        
        return {
                "Company Name": profile_data.get('Company Name', 'N/A'),
                "Symbol": symbol,
                "Sector": profile_data.get('Sector', 'N/A'),
                "Market Cap": profile_data['Financials'].get('Market Cap', '0'),
                "Beta": profile_data['Other Information'].get('Beta', '0'),

                "P/E Ratio": profile_data['Financials'].get('P/E Ratio (Trailing)', '0'),
                "Dividend Yield": profile_data['Financials'].get('Trailing Annual Dividend Yield', '0'),
                "Price to Book Ratio": profile_data['Financials'].get('Price to Book Ratio', '0'),
                "Liquidity Ratio": profile_data['Financial Health'].get('Current Ratio', '0'),
                "Debt to Equity Ratio": profile_data['Financial Health'].get('Debt to Equity Ratio', '0'),
                
                "Earnings Growth Rate": growthRate if growthRate else 0,
                "Uninterrupted Dividends": not Interrupted_Dividends,
                
                "Assets&Liabilities": Assets_Liabilities if Assets_Liabilities else [{ 'year': '---', 'assets': 0, 'liabilities': 0 }],
                "Close Prices": historical_price if historical_price else [{ 'time': '---', 'price': 0 }],

                "Total Non-Sharia Income": 0,
                "Total Interest-bearing Debt": 0,
                "Interest Income Percentage": 0,
                "Total Cash and Equivalents": 0,
                "Total Interest-bearing Investments": 0,
                "Non-Permissible Income Percentage": 0,
        }

    except Exception as e:
        handle_api_exception(e)
        raise CustomException(f"An error occurred while fetching company financial data: {str(e)}")



def format_market_cap(value):
    try:
        num = float(value)
    except ValueError:
        return value
    
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"


def round_if_numeric(value, decimals=2):
    if value == 'N/A':
        return 'N/A'

    try:
        numeric_value = float(value)
        return round(numeric_value, decimals)
    except ValueError:
        return 'N/A'




def clean_profile_data(profile_data):
    cleaned_data = {
        "Symbol": profile_data.get("symbol", "N/A"),
        "Company Name": profile_data.get("longName", "N/A"),
        "Sector": profile_data.get("sector", "N/A"),
        "Industry": profile_data.get("industry", "N/A"),
        "Website": profile_data.get("website", "N/A"),
        "Description": profile_data.get("longBusinessSummary", "N/A"),
        "Financials": {
            "Market Cap": format_market_cap(profile_data.get("marketCap", "N/A")),
            "Enterprise Value": format_market_cap(profile_data.get("enterpriseValue", "N/A")),
            "Profit Margin": f"{round_if_numeric(profile_data.get('profitMargins', 'N/A') * 100)}%" if profile_data.get('profitMargins') else 'N/A',
            "P/E Ratio (Trailing)": round_if_numeric(profile_data.get("trailingPE", "N/A")),
            "Dividend Rate": round_if_numeric(profile_data.get("dividendRate", "N/A")),
            "Trailing Annual Dividend Yield": f"{round_if_numeric(profile_data.get('trailingAnnualDividendYield', 'N/A') * 100)}%" if profile_data.get('trailingAnnualDividendYield') else 'N/A',
            "Payout Ratio": f"{round_if_numeric(profile_data.get('payoutRatio', 'N/A') * 100)}%" if profile_data.get('payoutRatio') else 'N/A',
            "Book Value": round_if_numeric(profile_data.get("bookValue", "N/A")),
            "Price to Book Ratio": round_if_numeric(profile_data.get("priceToBook", "N/A")),
            "Price to Sales (TTM)": round_if_numeric(profile_data.get("priceToSalesTrailing12Months", "N/A")),
            "Earnings Quarterly Growth": f"{round_if_numeric(profile_data.get('earningsQuarterlyGrowth', 'N/A') * 100)}%" if profile_data.get('earningsQuarterlyGrowth') else 'N/A',
            "Net Income to Common": format_market_cap(profile_data.get("netIncomeToCommon", "N/A")),
            "Trailing EPS": round_if_numeric(profile_data.get("trailingEps", "N/A")),
            "PEG Ratio": round_if_numeric(profile_data.get("pegRatio", "N/A")),
            "Gross Margins": f"{round_if_numeric(profile_data.get('grossMargins', 'N/A') * 100)}%" if profile_data.get('grossMargins') else 'N/A',
            "EBITDA Margins": f"{round_if_numeric(profile_data.get('ebitdaMargins', 'N/A') * 100)}%" if profile_data.get('ebitdaMargins') else 'N/A',
            "Operating Margins": f"{round_if_numeric(profile_data.get('operatingMargins', 'N/A') * 100)}%" if profile_data.get('operatingMargins') else 'N/A',
            "Return on Assets": f"{round_if_numeric(profile_data.get('returnOnAssets', 'N/A') * 100)}%" if profile_data.get('returnOnAssets') else 'N/A',
            "Return on Equity": f"{round_if_numeric(profile_data.get('returnOnEquity', 'N/A') * 100)}%" if profile_data.get('returnOnEquity') else 'N/A'
        },
        "Market Data": {
            "Current Price": round_if_numeric(profile_data.get("currentPrice", "N/A")),
            "Previous Close": round_if_numeric(profile_data.get("previousClose", "N/A")),
            "Open Price": round_if_numeric(profile_data.get("open", "N/A")),
            "Currency": profile_data.get("currency", "N/A")
        },
        "Dividend Information": {
            "Last Dividend Value": round_if_numeric(profile_data.get("lastDividendValue", "N/A")),
            "5-Year Avg Dividend Yield": f"{round_if_numeric(profile_data.get('fiveYearAvgDividendYield', 'N/A') * 100)}%" if profile_data.get('fiveYearAvgDividendYield') else 'N/A'
        },
        "Financial Health": {
            "Total Cash": format_market_cap(profile_data.get("totalCash", "N/A")),
            "Total Debt": format_market_cap(profile_data.get("totalDebt", "N/A")),
            "Quick Ratio": round_if_numeric(profile_data.get("quickRatio", "N/A")),
            "Current Ratio": round_if_numeric(profile_data.get("currentRatio", "N/A")),
            "Debt to Equity Ratio": round_if_numeric(profile_data.get("debtToEquity", "N/A")),
            "Revenue": format_market_cap(profile_data.get("totalRevenue", "N/A")),
        },
        "Other Information": {
            "Beta": round_if_numeric(profile_data.get("beta", "N/A")),
            "52-Week Change": f"{round_if_numeric(profile_data.get('52WeekChange', 'N/A') * 100)}%" if profile_data.get('52WeekChange') else 'N/A',
        }
    }

    return cleaned_data