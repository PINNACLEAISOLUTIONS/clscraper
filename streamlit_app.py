import asyncio
import streamlit as st
import craigslistscraper as cs
import pandas as pd

def main():
    st.set_page_config(
        page_title="CraigslistScraper Web App",
        page_icon="🚗",
        layout="wide"
    )
    
    st.title("🚗 CraigslistScraper Web App")
    st.markdown("Search Craigslist with an easy-to-use web interface!")
    
    # Sidebar for search parameters
    st.sidebar.header("Search Parameters")
    
    # Search inputs
    query = st.sidebar.text_input(
        "What are you searching for?", 
        placeholder="e.g., honda civic, iphone, apartment"
    )
    
    city = st.sidebar.selectbox(
        "Select City",
        [
            "newyork", "losangeles", "chicago", "houston", "phoenix", 
            "philadelphia", "sanantonio", "sandiego", "dallas", "sanjose",
            "austin", "jacksonville", "fortworth", "columbus", "charlotte",
            "sanfrancisco", "indianapolis", "seattle", "denver", "boston",
            "elpaso", "detroit", "nashville", "portland", "oklahomacity",
            "lasvegas", "memphis", "louisville", "baltimore", "milwaukee",
            "albuquerque", "tucson", "fresno", "mesa", "sacramento",
            "atlanta", "kansascity", "colorado", "omaha", "raleigh",
            "miami", "longbeach", "virginiabeach", "oakland", "minneapolis",
            "tulsa", "arlington", "neworleans", "wichita", "cleveland",
            "tampa", "bakersfield", "aurora", "anaheim", "honolulu"
        ]
    )
    
    category_options = {
        "for": "For Sale (General)",
        "cto": "Cars & Trucks - By Owner", 
        "ctd": "Cars & Trucks - By Dealer",
        "apa": "Apartments for Rent",
        "mob": "Mobile Phones",
        "ele": "Electronics",
        "boa": "Boats",
        "bik": "Bicycles",
        "mcy": "Motorcycles",
        "rvs": "RVs",
        "pts": "Car Parts",
        "wan": "Wanted",
        "zip": "Free Stuff"
    }
    
    category = st.sidebar.selectbox(
        "Category",
        list(category_options.keys()),
        format_func=lambda x: f"{x} - {category_options[x]}"
    )
    
    # Advanced filters
    st.sidebar.subheader("Filters (Optional)")
    
    # Price filters
    max_price = st.sidebar.number_input("Max Price ($)", min_value=0, value=0, step=100)
    min_price = st.sidebar.number_input("Min Price ($)", min_value=0, value=0, step=100)

    # Posting date filter
    posted_today = st.sidebar.checkbox("Posted Today Only")
    
    # Category filter
    has_image = st.sidebar.checkbox("Has Image")
    bundle_duplicates = st.sidebar.checkbox("Bundle Duplicates", value=True)
    
    # Search button
    search_button = st.sidebar.button("🔍 Search Craigslist", type="primary")
    
    # Main content area
    if search_button and query:
        with st.spinner(f"Searching for '{query}' in {city}..."):
            try:
                # Create search object
                search = cs.Search(
                    query=query,
                    city=city,
                    category=category
                )
                
                # Prepare filters
                filters = {}
                if max_price > 0:
                    filters["max_price"] = max_price
                if min_price > 0:
                    filters["min_price"] = min_price
                if posted_today:
                    filters["postedToday"] = 1
                if has_image:
                    filters["hasPic"] = 1
                if bundle_duplicates:
                    filters["bundleDuplicates"] = 1
                
                # Fetch results
                status = search.fetch(params=filters if filters else None)
                
                if status != 200:
                    st.error(f"Search failed (Status: {status})")

                    return
                
                # Display results
                num_ads = len(search.ads)
                st.success(f"Found {num_ads} ads!")
                
                if num_ads == 0:
                    st.info("No results found. Please adjust your search.")

                    return
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["List", "Table", "Detailed"])

                
                with tab1:
                    st.subheader("Search Results")
                    
                    # Display ads in a nice format
                    for i, ad in enumerate(search.ads[:20]):  # Limit to 20


                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{ad.title}**")
                                st.markdown(f"[View on Craigslist]({ad.url})")
                            
                            with col2:
                                if ad.price:
                                    st.markdown(f"💰 **${ad.price:,.0f}**")
                                else:
                                    st.markdown("💰 *Price not listed*")
                            
                            with col3:
                                if st.button("Get Details", key=f"detail_{i}"):
                                    with st.spinner("Fetching details..."):
                                        detail_status = ad.fetch()
                                        if detail_status == 200:
                                            st.json(ad.to_dict())
                                        else:
                                            st.error(f"Details fetch failed (Status: {detail_status})")

                            
                            st.divider()
                    
                    if num_ads > 20:
                        st.info(f"Showing first 20 of {num_ads} results")
                
                with tab2:
                    # Create DataFrame for table view
                    ads_data = []
                    for ad in search.ads[:50]:  # Limit to 50 for performance
                        ads_data.append({
                            "Title": ad.title,
                            "Price": f"${ad.price:,.0f}" if ad.price else "N/A" ,

                            "URL": ad.url
                        })
                    
                    df = pd.DataFrame(ads_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"craigslist_{query}_{city}.csv",
                        mime="text/csv"
                    )
                
                with tab3:
                    st.subheader("Detailed Analysis")
                    
                    # Get detailed info for first few ads asynchronously
                    async def fetch_ad_details(ad):
                        status = await ad.fetch_async()
                        if status == 200:
                            return ad.to_dict()
                        return None

                    async def display_ad_details(ads):
                        detailed_ads = [await ad_data for ad_data in asyncio.as_completed([fetch_ad_details(ad) for ad in ads])]
                        detailed_ads = [ad for ad in detailed_ads if ad is not None]
                        if detailed_ads:
                            for i, ad_data in enumerate(detailed_ads):
                                with st.expander(f"Ad {i+1}: {ad_data.get('title', 'No title')}"):
                                    st.json(ad_data)
                        else:
                            st.warning("Could not fetch detailed information for ads")

                    if search and search.ads:
                        with st.spinner("Fetching ad details..."):
                            asyncio.run(display_ad_details(search.ads[:5]))
                    else:
                        st.info("No ads found.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    elif search_button and not query:
        st.warning("Please enter a search query!")
    
    # Instructions
    if not search_button:
        st.markdown("""
        ### How to use this app:
        
        1. Enter your search query (e.g., "honda civic", "iphone").
        2. Select a city from the dropdown
        3. Choose a category that matches what you're looking for
        4. Optionally set filters like price range or posting date
        5. Click the Search button to find listings
        
        ### Features:
        - List View: Browse results with clickable links
        - Table View: See results in a sortable table and download as CSV
        - Detailed View: Get complete information for the first few ads
        
        ### Tips:
        - Use specific search terms for better results
        - Try different cities to compare prices
        - Use filters to narrow down results
        - Click "Get Details" for more information about specific ads
        """)
        

    if __name__ == "__main__":
        main()