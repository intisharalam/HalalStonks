import httpx
import os
import yfinance as yf
from exceptions import handle_api_exception, CustomException
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables from .env file
load_dotenv()

STOCK_API_KEY = 'gJK3pAifqyVdjbMMoDy6bWQyyIHoBxFE'
#print(STOCK_API_KEY)

NEWS_API_KEY = 'FwWJ7UpulXL_blpe3AEOlkBWzSKIxP4NVfvHH_jeYPkVem9f'


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

        

        # Check halal stock criteria
        halal_criteria_results, halal_score = await check_halal_stock(symbol)



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

                "Halal Stock Criteria Results": halal_criteria_results if halal_criteria_results else [False,False,False,False,False],
                "Halal Score": halal_score if halal_score else 0
        }

    except Exception as e:
        handle_api_exception(e)
        raise CustomException(f"An error occurred while fetching company financial data: {str(e)}")


async def check_halal_stock(ticker):
    try:
        # Fetch annual financial data
        balance_sheet, income_statement, info = get_annual_financials(ticker)

        # Initialize variables to track results
        criteria_results = []
        score = 0
        
        # Check Criteria 1
        result_criteria_1 = check_haram_industry(info)
        criteria_results.append(result_criteria_1)
        if result_criteria_1:
            score += 1
        
        # Check Criteria 2
        result_criteria_2 = check_haram_income(income_statement)
        criteria_results.append(result_criteria_2)
        if result_criteria_2:
            score += 1
        
        # Check Criteria 3
        result_criteria_3 = check_interest_bearing_debt_to_assets(balance_sheet, income_statement)
        criteria_results.append(result_criteria_3)
        if result_criteria_3:
            score += 1
        
        # Check Criteria 4
        result_criteria_4 = check_illiquid_assets_ratio(balance_sheet)
        criteria_results.append(result_criteria_4)
        if result_criteria_4:
            score += 1
        
        # Check Criteria 5
        result_criteria_5 = check_net_liquid_assets_vs_market_cap(balance_sheet, info)
        criteria_results.append(result_criteria_5)
        if result_criteria_5:
            score += 1
        
        # Return results and score
        return criteria_results, score
    
    except Exception as e:
        raise CustomException(f"Error checking halal stock criteria: {str(e)}")




def get_annual_financials(ticker):
    # Fetch data from Yahoo Finance for the past year (annual data)
    stock = yf.Ticker(ticker)
    
    balance_sheet = stock.balance_sheet
    financials = stock.financials  # Transpose to have years as rows
    info = stock.info

    # Convert to pandas DataFrame
    balance_sheet = pd.DataFrame(balance_sheet)
    financials = pd.DataFrame(financials)
    
    balance_sheet = balance_sheet.iloc[:, 0]
    financials = financials.iloc[:, 0]

    # Set pandas display options to show all rows and columns
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    
    return [balance_sheet, financials, info]

def check_haram_industry(info):

    industry = info.get('industry', '')
    
    print(f"Industry: {industry}")
    # List of haram industries
    haram_industries = [
        "Beverages - Brewers", "Beverages - Wineries & Distilleries", "Beverages - Non-Alcoholic", 
        "Confectioners", "Gambling", "Casinos", "Banks—Diversified", "Banks—Regional", "Credit Services", 
        "Mortgage Finance", "Entertainment", "Broadcasting", "Tobacco", "Alcohol-related industries",
        "Interest-based financial services", "Certain entertainment sectors"
    ]
    # Criteria 1: Business of the company
    for keyword in haram_industries:
        if keyword in industry:
            print(f"Criterion 1: Not halal due to haram industry: {keyword}")
            return False  # Not halal due to haram industry
    
    return True

def check_haram_income(financials):
    # Criteria 2: Income from non-sharia compliant investments
    income_from_haram_sources = [
    'Interest Expense',
    'Earnings From Equity Interest',
    'Net Interest Income',
    'Interest Income Non Operating',
    'Net Non Operating Interest Income Expense',
    'Interest Income'
    ]


    total_haram_income = 0    
    # Total Revenue for the latest year (assuming last column is latest)
    total_revenue = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else 0    
    
    # Loop through each metric and print its value if it exists in the DataFrame
    for haram_income in income_from_haram_sources:
        if haram_income in financials.index:
            value = financials.loc[haram_income]
            total_haram_income += value
            #print(f"{haram_income}: {financials.loc[haram_income]}")
        else:
            pass
            #print(f"{haram_income}: Not found")  # Handle case where metric doesn't exist in the DataFrame


    #print(f"Total Revenue: {total_revenue}")
    #print(f"Total Haram Income: {total_haram_income}")
    
    if total_revenue > 0 and (total_haram_income / total_revenue) > 0.05:
        print(f"Criterion 2: Not halal due to excessive income from haram sources. {total_haram_income / total_revenue} > 0.05")
        return False  # Not halal due to excessive income from haram sources
    
    return True

def check_interest_bearing_debt_to_assets(balance_sheet, income_statement):
    # Extract total assets from balance sheet
    total_assets = balance_sheet.get('Total Assets', 0)
    #print(f"Total Assets: {total_assets}")
    
    # Extract interest-bearing debt from balance sheet and income statement
    current_debt = balance_sheet.get('Current Debt And Capital Lease Obligation', 0)
    #print(f"Current Debt: {current_debt}")
    long_term_debt = balance_sheet.get('Long Term Debt And Capital Lease Obligation', 0)
    #print(f"Long Term Debt: {long_term_debt}")
    interest_expense = income_statement.get('Interest Expense', 0)
    #print(f"Interest Expence: {interest_expense}")
    interest_expense_non_operating = income_statement.get('Interest Expense Non Operating', 0)
    #print(f"Interest Expence: {interest_expense}")
    
    # Calculate total interest-bearing debt
    total_interest_bearing_debt = current_debt + long_term_debt + interest_expense + interest_expense_non_operating
    
    if total_assets > 0 and (total_interest_bearing_debt / total_assets) > 0.33:
        print(f"Criterion 3: Not halal due to excessive interest-bearing debt. {(total_interest_bearing_debt / total_assets)} > 0.33")
        return False  # Not halal due to excessive interest-bearing debt
    
    return True

def check_illiquid_assets_ratio(balance_sheet):
    # Extract total assets from the balance sheet
    total_assets = balance_sheet.get('Total Assets', 0)
    #print(total_assets)
    
    # Extract illiquid assets from the balance sheet
    illiquid_assets_items = [
        'Buildings And Improvements',
        'Net PPE',
        'Investment Properties',
        'Machinery Furniture Equipment',
        'Other Properties',
        'Land And Improvements',
        'Investmentin Financial Assets',
        'Investments And Advances',
        'Investmentsin Subsidiariesat Cost',
        'Investmentsin Associatesat Cost'
    ]
    
    # Sum the values of the illiquid assets
    illiquid_assets = sum(balance_sheet.get(item, 0) for item in illiquid_assets_items)
    #print(illiquid_assets)

    #print((illiquid_assets / total_assets))
    
    # Check if we have any illiquid assets data
    if not illiquid_assets:
        print("Criterion 4: Insufficient data to determine illiquid assets.")
        return True  # Assuming it's halal due to lack of data
    
    # Calculate the illiquid assets ratio
    if total_assets > 0 and (illiquid_assets / total_assets) < 0.20:
        print(f"Criterion 4: Not halal due to insufficient illiquid assets. {(illiquid_assets / total_assets)} < 0.20")
        return False  # Not halal due to insufficient illiquid assets
    
    return True

def check_net_liquid_assets_vs_market_cap(balance_sheet, info):
    # Extract relevant items for net liquid assets calculation
    cash_and_cash_equivalents = balance_sheet.get('Cash And Cash Equivalents', 0)
    short_term_investments = balance_sheet.get('Short-Term Investments', 0)
    other_short_term_investments = balance_sheet.get('Other Short-Term Investments', 0)
    accounts_receivable = balance_sheet.get('Accounts Receivable', 0)
    inventory = balance_sheet.get('Inventory', 0)
    other_current_assets = balance_sheet.get('Other Current Assets', 0)
    net_ppe = balance_sheet.get('Net PPE', 0)
    other_long_term_assets = balance_sheet.get('Other Long-Term Assets', 0)
    
    # Calculate total liquid assets
    total_liquid_assets = (
        cash_and_cash_equivalents + 
        short_term_investments + 
        other_short_term_investments + 
        accounts_receivable + 
        other_current_assets
    )
    
    # Calculate tangible fixed assets
    tangible_fixed_assets = net_ppe + inventory + other_long_term_assets
    
    # Calculate total assets and liabilities
    total_assets = balance_sheet.get('Total Assets', 0)
    total_liabilities = balance_sheet.get('Total Liabilities Net Minority Interest', 0)
    
    # Calculate net liquid assets
    net_liquid_assets = total_liquid_assets - total_liabilities - tangible_fixed_assets

    # Fetch market capitalization from info dictionary
    market_cap = info.get('marketCap', 0)

    # Compare net liquid assets with market capitalization
    if net_liquid_assets > market_cap:
        print("Criterion 5: Not halal due to excess net liquid assets compared to market capitalization.")
        return False  # Not halal due to excess net liquid assets
    
    return True



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