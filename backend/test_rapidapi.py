import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

URL = "https://real-time-product-search.p.rapidapi.com/search"
HEADERS = {
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com"
}

def test_sort(sort_value: str):

    params = {
        "q": "oversized cargo pants streetwear",
        "country": "us",
        "language": "en",
        "limit": "2",
        "sort_by": sort_value
    }

    response = requests.get(URL, headers=HEADERS, params=params)
    products = response.json().get("data", {}).get("products", [])

    # Print the price of first result to see if sorting is working
    if products:
        price = products[0].get("offer", {}).get("price", "no price")
        title = products[0].get("product_title", "no title")
        print(f"sort_by={sort_value} → first result: {title} | {price}")
    else:
        print(f"sort_by={sort_value} → no results or error (status: {response.status_code})")

# Test all sort options
test_sort("BEST_MATCH")
test_sort("LOWEST_PRICE")
test_sort("HIGHEST_PRICE")
test_sort("TOP_RATED")
test_sort("NEWEST")