import streamlit as st
import craigslistscraper as cs
import pandas as pd
import time
from datetime import datetime


# Configure page
st.set_page_config(
    page_title="CraigslistScraper - Search Craigslist Easily",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
    .ad-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def search_craigslist(query, city, category, filters=None):
    """Cached function to search Craigslist"""
    try:
        search = cs.Search(query=query, city=city, category=category)
        status = search.fetch(params=filters)
        
        if status == 200:
            return search.ads, status, None
        else:
            return [], status, f"Search failed with status {status}"
    except Exception as e:
        return [], 500, str(e)


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_ad_details(ad_url):
    """Cached function to get ad details"""
    try:
        ad = cs.Ad(url=ad_url)
        status = ad.fetch()
        if status == 200:
            return ad.to_dict(), status, None
        else:
            return None, status, f"Failed to fetch ad details"
    except Exception as e:
        return None, 500, str(e)


def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 CraigslistScraper</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 18px;">Search Craigslist listings from across the United States with ease!</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Search Configuration")
    
    # Search inputs
    query = st.sidebar.text_input(
        "🔍 Search Query",
        placeholder="e.g., honda civic, iphone 15, apartment",
        help="Enter what you're looking for"
    )
    
    # City selection with popular cities first
    popular_cities = ["newyork", "losangeles", "chicago", "houston", "phoenix", "philadelphia"]
    other_cities = [
        "sanantonio", "sandiego", "dallas", "sanjose", "austin", "jacksonville",
        "fortworth", "columbus", "charlotte", "sanfrancisco", "indianapolis",
        "seattle", "denver", "boston", "elpaso", "detroit", "nashville",
        "portland", "oklahomacity", "lasvegas", "memphis", "louisville",
        "baltimore", "milwaukee", "albuquerque", "tucson", "fresno", "mesa",
        "sacramento", "atlanta", "kansascity", "colorado", "omaha", "raleigh",
        "miami", "longbeach", "virginiabeach", "oakland", "minneapolis",
        "tulsa", "arlington", "neworleans", "wichita", "cleveland", "tampa",
        "bakersfield", "aurora", "anaheim", "honolulu"
    ]
    
    all_cities = popular_cities + other_cities
    
    city = st.sidebar.selectbox(
        "🏙️ City",
        all_cities,
        help="Select the city to search in"
    )
    
    # Category selection
    category_options = {
        "for": "🛍️ For Sale (General)",
        "cto": "🚗 Cars & Trucks - By Owner",
        "ctd": "🏪 Cars & Trucks - By Dealer",
        "apa": "🏠 Apartments for Rent",
        "mob": "📱 Mobile Phones",
        "ele": "🔌 Electronics",
        "boa": "⛵ Boats",
        "bik": "🚴 Bicycles",
        "mcy": "🏍️ Motorcycles",
        "rvs": "🚐 RVs",
        "pts": "🔧 Car Parts",
        "wan": "❓ Wanted",
        "zip": "🆓 Free Stuff"
    }
    
    category = st.sidebar.selectbox(
        "📂 Category",
        list(category_options.keys()),
        format_func=lambda x: category_options[x],
        help="Choose the category that best matches your search"
    )
    
    # Advanced filters in an expander
    with st.sidebar.expander("🎛️ Advanced Filters"):
        max_price = st.number_input(
            "💰 Max Price ($)",
            min_value=0,
            value=0,
            step=100,
            help="0 = no limit"
        )
        min_price = st.number_input(
            "💰 Min Price ($)",
            min_value=0,
            value=0,
            step=100,
            help="0 = no limit"
        )
        posted_today = st.checkbox("📅 Posted Today Only")
        has_image = st.checkbox("🖼️ Has Image")
        bundle_duplicates = st.checkbox("📦 Bundle Duplicates", value=True)
    
    # Search button
    search_button = st.sidebar.button("🔍 Search Craigslist", type="primary")
    
    # Info about the app
    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        **CraigslistScraper** helps you search Craigslist listings efficiently.
        
        🚀 **Features:**
        - Search multiple cities
        - Filter by price, date, images
        - Export results to CSV
        - Get detailed ad information
        
        ⚠️ **Note:** This tool is for personal use only.
        """)
    
    # Main content
    if not search_button:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🚀 Welcome to CraigslistScraper!
            
            **How to get started:**
            
            1. 🔍 Enter your search query in the sidebar
            2. 🏙️ Select a city to search in
            3. 📂 Choose the appropriate category
            4. 🎛️ Optionally set filters for better results
            5. 🔍 Click "Search Craigslist" to find listings
            
            ### 🌟 Features:
            - **Multi-city search**: Browse listings from 50+ US cities
            - **Smart filtering**: Filter by price, posting date, and more
            - **Export data**: Download results as CSV for analysis
            - **Detailed views**: Get complete information about listings
            - **Fast & reliable**: Cached results for better performance
            
            ### 📊 Popular Searches:
            Try searching for: `honda civic`, `iphone`, `apartment`, `bicycle`, `furniture`
            """)
    
    elif query:
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
        
        # Search progress
        with st.spinner(f"🔍 Searching for '{query}' in {city.title()}..."):
            start_time = time.time()
            ads, status, error = search_craigslist(
                query, city, category, filters if filters else None
            )
            search_time = time.time() - start_time
        
        if error:
            st.error(f"❌ Search failed: {error}")
            return
        
        # Results header
        num_ads = len(ads)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Results Found", num_ads)
        with col2:
            st.metric("🏙️ City", city.title())
        with col3:
            st.metric("📂 Category", category.upper())
        with col4:
            st.metric("⏱️ Search Time", f"{search_time:.2f}s")
        
        if num_ads == 0:
            st.warning("🤷‍♂️ No results found. Try adjusting your search terms or filters.")
            st.info("💡 **Tips:** Try broader search terms, remove filters, or search in a different city.")
            return
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📋 Browse Results", "📊 Data Table", "📈 Analytics"])
        
        with tab1:
            st.subheader(f"📋 Found {num_ads} listings")
            
            # Results per page
            results_per_page = st.selectbox("Results per page:", [10, 20, 50], index=1)
            total_pages = (num_ads + results_per_page - 1) // results_per_page
            
            if total_pages > 1:
                page = st.selectbox("Page:", range(1, total_pages + 1))
                start_idx = (page - 1) * results_per_page
                end_idx = min(start_idx + results_per_page, num_ads)
                page_ads = ads[start_idx:end_idx]
                st.info(f"Showing results {start_idx + 1}-{end_idx} of {num_ads}")
            else:
                page_ads = ads[:results_per_page]
            
            # Display ads
            for i, ad in enumerate(page_ads):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{ad.title}**")
                        if ad.price:
                            st.markdown(f"💰 **${ad.price:,.0f}**")
                        else:
                            st.markdown("💰 *Price not listed*")
                        st.markdown(f"🔗 [View on Craigslist]({ad.url})")
                    
                    with col2:
                        if st.button(f"📄 Get Details", key=f"detail_{i}"):
                            with st.spinner("Fetching details..."):
                                details, detail_status, detail_error = get_ad_details(ad.url)
                                if details:
                                    st.json(details)
                                else:
                                    st.error(f"❌ {detail_error}")
                    
                    st.divider()
        
        with tab2:
            st.subheader("📊 Results Table")
            
            # Create DataFrame
            ads_data = []
            for ad in ads:
                ads_data.append({
                    "Title": ad.title,
                    "Price": ad.price if ad.price else 0,
                    "Price_Display": f"${ad.price:,.0f}" if ad.price else "N/A",
                    "URL": ad.url
                })
            
            df = pd.DataFrame(ads_data)
            
            # Display options
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("Sort by:", ["Title", "Price", "Price_Display"])
            with col2:
                ascending = st.checkbox("Ascending order", value=True)
            
            # Sort and display
            if sort_by == "Price":
                df_display = df.sort_values("Price", ascending=ascending)
            else:
                df_display = df.sort_values(sort_by, ascending=ascending)
            
            # Show table without internal Price column
            display_df = df_display[["Title", "Price_Display", "URL"]].rename(
                columns={"Price_Display": "Price"}
            )
            st.dataframe(display_df, use_container_width=True)
            
            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"craigslist_{query}_{city}_{timestamp}.csv",
                mime="text/csv"
            )
        
        with tab3:
            st.subheader("📈 Search Analytics")
            
            # Price analytics
            prices = [ad.price for ad in ads if ad.price and ad.price > 0]
            
            if prices:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Average Price", f"${sum(prices)/len(prices):,.0f}")
                with col2:
                    st.metric("💰 Median Price", f"${sorted(prices)[len(prices)//2]:,.0f}")
                with col3:
                    st.metric("💰 Price Range", f"${min(prices):,.0f} - ${max(prices):,.0f}")
                
                # Price distribution
                price_df = pd.DataFrame({"Price": prices})
                st.subheader("💹 Price Distribution")
                st.bar_chart(price_df["Price"].value_counts().head(20))
            else:
                st.info("📊 No pricing data available for analysis.")
            
            # Other stats
            st.subheader("📊 Listing Statistics")
            with_price = len([ad for ad in ads if ad.price])
            without_price = num_ads - with_price
            
            stats_data = {
                "Category": ["With Price", "Without Price"],
                "Count": [with_price, without_price]
            }
            stats_df = pd.DataFrame(stats_data)
            st.bar_chart(stats_df.set_index("Category"))
    
    else:
        st.warning("🔍 Please enter a search query to get started!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>"
        "🔍 CraigslistScraper | Built with Streamlit | For personal use only"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()