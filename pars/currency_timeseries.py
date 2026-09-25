import os
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

fred = Fred(api_key=FRED_API_KEY)

df = fred.get_series("DEXCAUS").to_frame()

df.to_csv("data/currency.csv", header=True)