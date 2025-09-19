import streamlit as st
import craigslistscraper as cs
import pandas as pd
import time
from datetime import datetime
from spellchecker import SpellChecker


# Configure page
st.set_page_config(
    page_title="Pinnacle AI Solutions Craigslist Scraper",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #181825 0%, #232946 100%);
    }

    /* Main header with a new font and shadow */
    .main-header {
        font-family: 'Arial Black', Gadget, sans-serif;
        text-align: center;
        color: #1e3a8a; /* Dark Blue */
        text-shadow: 2px 2px 5px #cccccc;
        margin-bottom: 30px;
    }

    /* Sidebar styling with a new gradient */
    .css-1d391kg { /* This is a common class for the sidebar */
        background: linear-gradient(180deg, #e0c3fc 0%, #8ec5fc 100%);
        border-right: 2px solid #ffffff;
    }

    /* Primary button with a vibrant gradient */
    .stButton > button {
        width: 100%;
        background-image: linear-gradient(to right, #ff8177 0%, #ff867a 0%, #ff8c7f 21%, #f99185 52%, #cf556c 78%, #b12a5b 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: bold;
        box-shadow: 0 4px 15px 0 rgba(252, 102, 117, 0.75);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-image: linear-gradient(to right, #b12a5b 0%, #cf556c 22%, #f99185 48%, #ff8c7f 78%, #ff867a 100%);
        box-shadow: 0 2px 10px 0 rgba(252, 102, 117, 0.75);
    }

    /* Ad container with a new border color */
    .ad-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border-left: 5px solid #ff8177; /* Vibrant pink/red */
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .ad-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }

    /* Metric cards with a fresh look */
    .stMetric {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-top: 5px solid #8ec5fc; /* Light Blue */
    }

    /* Styling for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #eee;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #ff8177;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def search_craigslist(
    query: str,
    location: str,
    category: str,
    sort_by: str = "date",
    filters: dict | None = None
) -> tuple[list, int, str | None]:
    """Searches Craigslist for a given city."""
    try:
        search = cs.Search(query=query, city=location, category=category)
        status = search.fetch(sort_by=sort_by, params=filters)
        if status == 200:
            return search.ads, status, None
        else:
            return [], status, f"Search failed with status {status}"

    except Exception as e:
        return [], 500, f"An unexpected error occurred: {e}"



@st.cache_data(ttl=600)
def get_ad_details(ad_url: str) -> tuple[dict | None, int, str]:
    """Fetches and caches ad details, handling errors gracefully."""
    try:
        ad = cs.Ad(url=ad_url)
        status = ad.fetch()
        if status == 200:
            return ad.to_dict(), status, None
        else:
            return None, status, f"Failed to fetch ad details: Status code {status}"
    except Exception as e:
        return None, 500, f"An unexpected error occurred: {e}"



@st.cache_data(ttl=3600)
def get_all_cities() -> list:
    """Efficiently reads and caches all city hostnames."""
    import json
    try:
        with open('craigslistscraper/data/areas.json', 'r') as f:
            areas = json.load(f)
        # Use a set for uniqueness and then sort for consistent ordering
        cities = sorted(list(set(area['Hostname'] for area in areas)))
        return cities
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error loading city data: {e}")
        return []


def main():
    # Header
    st.markdown('<h1 class="main-header">PINNACLE AI SOLUTIONS CRAIGSLIST SCRAPER</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 18px;">Search Craigslist listings from across the United States with ease!</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Search Configuration")
    
    # Search inputs
    query = st.sidebar.text_input(
        "🔍 Search Query",
        placeholder="e.g., honda civic, iphone 15, apartment",
        help="Enter what you're looking for"
    )
    
    # Spell check the query
    if query:
        spell = SpellChecker()
        # Split query into words to check each one
        words = query.split()
        misspelled = spell.unknown(words)
        
        if misspelled:
            corrected_words = []
            for word in words:
                # Get the best correction
                correction = spell.correction(word)
                corrected_words.append(correction if correction is not None else word)

            corrected_query = " ".join(corrected_words)
            
            # Show a suggestion if the correction is different
            if corrected_query.lower() != query.lower():
                st.sidebar.info(f"Did you mean: **{corrected_query}**?")

    # Location selection
    all_cities = get_all_cities()
    city = st.sidebar.selectbox(
        "🏙️ City",
        [""] + all_cities,
        help="Select the city to search in"
    )

    location = city
    
    
    search_type = st.sidebar.radio(
        "Select Search Type",
        ('For Sale', 'Services', 'Jobs')
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
        "atq": "🏺 Antiques - By Owner",
        "atd": "🏺 Antiques - By Dealer",
        "tls": "🛠️ Tools - By Owner",
        "tld": "🛠️ Tools - By Dealer",
        "wan": "❓ Wanted",
        "zip": "🆓 Free Stuff",
    }

    service_options = {
        "biz": "💼 Small Biz Ads",
        "cps": "💻 Computer Services",
        "crs": "🎨 Creative Services",
        "evs": "🎉 Event Services",
        "hss": "🏡 Household Services",
        "lss": "🎓 Lessons & Tutoring",
        "lbs": "🚚 Labor / Hauling / Moving",
        "sks": "🛠️ Skilled Trade Services",
        "lgs": "⚖️ Legal Services",
        "fns": "💰 Financial Services",
        "rts": "🏘️ Real Estate Services",
        "aos": "🚗 Automotive Services",
        "bts": "💅 Beauty Services",
        "wet": "✍️ Writing / Editing / Translation",
        "trv": "✈️ Travel/Vacation Services",
        "fgs": "🌿 Farm & Garden Services",
        "pas": "🐾 Pet Services",
        "mas": "⚓ Marine Services",
        "cys": "🚲 Cycle Services",
        "cms": "📱 Cell Phone / Mobile Services",
        "hws": "🌿 Health/Wellness Services"
    }

    job_options = {
        "web": "🌐 Web/HTML/Info Design",
        "bus": "📈 Business/Mgmt",
        "mar": "📢 Marketing/Advertising/PR",
        "etc": " miscellaneous",
        "wri": "✍️ Writing/Editing",
        "sof": "💻 Software/QA/DBA/etc",
        "acc": "💰 Accounting/Finance",
        "ofc": "📄 Admin/Office",
        "med": "🎨 Art/Media/Design",
        "hea": "⚕️ Healthcare",
        "ret": "🛒 Retail/Wholesale",
        "npo": "🤝 Nonprofit",
        "lgl": "⚖️ Legal/Paralegal",
        "egr": "🏗️ Architect/Engineer/CAD",
        "sls": "💲 Sales",
        "sad": "💻 Systems/Networking",
        "tfr": "🎬 TV/Film/Video/Radio",
        "hum": "👥 Human Resource",
        "tch": "👨‍🏫 Technical Support",
        "edu": "🎓 Education/Teaching",
        "trd": "🛠️ Skilled Trades/Artisan",
        "gov": "🏛️ Government",
        "trp": "🚚 Transportation",
        "spa": "💆 Salon/Spa/Fitness",
        "rej": "🏘️ Real Estate",
        "mnu": "🏭 Manufacturing",
        "fbh": "🍔 Food/Beverage/Hospitality",
        "lab": "👷 General Labor",
        "sec": "🛡️ Security"
    }

    if search_type == 'For Sale':
        category = st.sidebar.selectbox(
            "📂 Category",
            list(category_options.keys()),
            format_func=lambda x: category_options[x],
            help="Choose the category that best matches your search"
        )
    elif search_type == 'Services':
        category = st.sidebar.selectbox(
            "📂 Category",
            list(service_options.keys()),
            format_func=lambda x: service_options[x],
            help="Choose the service category"
        )
    else: # Jobs
        category = st.sidebar.selectbox(
            "📂 Category",
            list(job_options.keys()),
            format_func=lambda x: job_options[x],
            help="Choose the job category"
        )
    
    # Advanced filters in an expander
    with st.sidebar.expander("🎛️ Advanced Filters"):
        sort_by = st.selectbox(
            "Sort by",
            [("date (newest)", "date"), ("price (ascending)", "priceasc"), ("price (descending)", "pricedsc")],
            format_func=lambda x: x[0]
        )[1]
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
    if search_button:
        if not location:
            st.sidebar.error("Please select a city or a state to search in.")
            st.stop()

        # Prepare filters using dictionary comprehension for conciseness and readability
        filters = {
            "max_price": max_price if max_price > 0 else None,
            "min_price": min_price if min_price > 0 else None,
            "postedToday": 1 if posted_today else None,
            "hasPic": 1 if has_image else None,
            "bundleDuplicates": 1 if bundle_duplicates else None,
        }
        # Remove None values from the filters dictionary
        filters = {k: v for k, v in filters.items() if v is not None}

        # Search progress
        search_description = f"'{query}'" if query else "all listings"
        with st.spinner(f"🔍 Searching for {search_description} in {location.title()}..."):
            start_time = time.time()
            ads, status, error = search_craigslist(
                query, location, category, sort_by=sort_by, filters=filters or None
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
            st.metric("🏙️ Location", location.title())
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
                    # Fetch details first to get image URL
                    details, detail_status, detail_error = get_ad_details(ad.url)
                    
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        image_url = "https://via.placeholder.com/150"
                        if details and details.get("image_urls"):
                            image_url = details["image_urls"][0]
                        st.image(image_url, width=150)

                    with col2:
                        st.subheader(ad.title)
                        st.markdown(f"**Price:** {f'${ad.price:,.0f}' if ad.price else 'N/A'}")
                        st.markdown(f'[View on Craigslist]({ad.url})')

                    with st.expander("More Info & Details"):
                        if details:
                            st.json(details)
                        else:
                            st.error(f"❌ Could not fetch details: {detail_error}")
        
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
                sort_by_col = st.selectbox("Sort by:", ["Title", "Price", "Price_Display"])
            with col2:
                ascending = st.checkbox("Ascending order", value=True)
            
            # Sort and display
            if sort_by_col == "Price":
                df_display = df.sort_values("Price", ascending=ascending)
            else:
                df_display = df.sort_values(sort_by_col, ascending=ascending)
            
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
                file_name=f"craigslist_{query or 'all'}_{location}_{timestamp}.csv",
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
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🚀 Welcome to CraigslistScraper!
            
            **How to get started:**
            
            1. 🔍 Enter your search query in the sidebar (or leave blank to browse a category)
            2. 🏙️ Select a city or state to search in
            3. 📂 Choose the appropriate category
            4. 🎛️ Optionally set filters for better results
            5. 🔍 Click "Search Craigslist" to find listings
            
            ### 🌟 Features:
            - **Multi-city & State-wide search**: Browse listings from 50+ US cities or entire states
            - **Smart filtering**: Filter by price, posting date, and more
            - **Export data**: Download results as CSV for analysis
            - **Detailed views**: Get complete information about listings
            - **Fast & reliable**: Cached results for better performance
            
            ### 📊 Popular Searches:
            Try searching for: `honda civic`, `iphone`, `apartment`, `bicycle`, `furniture`
            """)
    
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