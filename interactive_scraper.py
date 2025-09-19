import craigslistscraper as cs
import json

def main():
    print("🚗 CraigslistScraper Interactive Tool 🚗")
    print("=" * 50)
    
    # Get user input
    query = input("What are you searching for? (e.g., 'honda civic', 'iphone', 'apartment'): ")
    city = input("Which city? (e.g., 'newyork', 'losangeles', 'chicago', 'minneapolis'): ")
    
    print("\nAvailable categories:")
    print("- cto (cars & trucks - by owner)")
    print("- ctd (cars & trucks - by dealer)")
    print("- apa (apartments for rent)")
    print("- mob (mobile phones)")
    print("- ele (electronics)")
    print("- for (for sale)")
    
    category = input("Category (default: for): ").strip() or "for"
    
    print(f"\n🔍 Searching for '{query}' in {city}...")
    print("-" * 50)
    
    # Create and execute search
    search = cs.Search(
        query=query,
        city=city,
        category=category
    )
    
    try:
        status = search.fetch()
        if status != 200:
            print(f"❌ Error: Unable to fetch search (status: {status})")
            return
        
        print(f"✅ Found {len(search.ads)} ads!")
        
        if len(search.ads) == 0:
            print("No results found. Try a different search term or city.")
            return
        
        # Show first 10 ads
        for i, ad in enumerate(search.ads[:10]):
            print(f"\n📋 Ad {i+1}:")
            print(f"   Title: {ad.title}")
            print(f"   Price: ${ad.price}" if ad.price else "   Price: Not specified")
            print(f"   URL: {ad.url}")
        
        if len(search.ads) > 10:
            print(f"\n... and {len(search.ads) - 10} more ads")
        
        # Ask if user wants detailed info
        detail = input(f"\nGet detailed info for first ad? (y/n): ").lower()
        if detail == 'y' and len(search.ads) > 0:
            print("\n📄 Fetching detailed information...")
            first_ad = search.ads[0]
            status = first_ad.fetch()
            if status == 200:
                data = first_ad.to_dict()
                print(json.dumps(data, indent=2))
            else:
                print(f"❌ Could not fetch details (status: {status})")
                
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()