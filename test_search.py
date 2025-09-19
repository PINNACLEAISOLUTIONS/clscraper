import craigslistscraper as cs
import json

# Define a broader search that's more likely to have results
search = cs.Search(
    query = "honda",
    city = "newyork",
    category = "cto"
)

# Fetch the html from the server
status = search.fetch()
if status != 200:
    raise Exception(f"Unable to fetch search with status <{status}>.")

print(f"{len(search.ads)} ads found!")

# Show first few ads if any found
for i, ad in enumerate(search.ads[:3]):  # Limit to first 3 ads
    print(f"\nAd {i+1}: {ad.title}")
    print(f"URL: {ad.url}")
    print(f"Price: {ad.price}")
    
    # Optionally fetch full ad details (this makes additional requests)
    # status = ad.fetch()
    # if status == 200:
    #     data = ad.to_dict()
    #     print(json.dumps(data, indent=2))