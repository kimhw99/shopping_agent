from serpapi import GoogleSearch

api_key=""

def product_search_query(intent):
    
    name = intent["category"] or ""

    # price
    if intent["filters"]["price_min"] is not None:
        if intent["filters"]["price_max"] is not None:
            price = f"between ${intent["filters"]["price_min"]} and ${intent["filters"]["price_max"]}"

        else:
            price = f"over ${intent["filters"]["price_min"]}"

    else:
        if intent["filters"]["price_max"] is not None:
            price = f"below ${intent["filters"]["price_max"]}"

        else:
            price = ""

    # brand
    if intent["filters"]["brand"] is not None:
        brand = " OR ".join(intent["filters"]["brand"])

    else:
        brand = ""

    # brand
    if intent["filters"]["attributes"] is not None:
        features = " ".join(intent["filters"]["attributes"])

    else:
        features = ""

    return " ".join([features, brand, name, price])

def product_search(intent, api_key=api_key):

    if type(intent) == dict:
        query = product_search_query(intent)

    elif type(intent) == str:
        query = intent

    else:
        query = str(intent)

    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    shopping_results = results.get("shopping_results", [])

    # title
    # product_link
    # price
    # rating
    # reviews
    # source (store)
    
    return shopping_results

def compare_search(items, api_key=api_key):

    compare_results = []
    for i in items:
        params = {
            "engine": "google_shopping",
            "q": i,
            "hl": "en",
            "gl": "us",
            "api_key": api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        shopping_results = results.get("shopping_results", [])
        compare_results.append(shopping_results[0])

    # title
    # product_link
    # price
    # rating
    # reviews
    # source (store)
    
    return compare_results