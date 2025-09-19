from bs4 import BeautifulSoup, Tag
import requests
import re
from typing import Union, List, Dict, Optional

from .ad import Ad
from .utils import format_price, build_url


class Search:
    def __init__(self, query: str, city: str, category: str = "sss") -> None:
        """An abstraction for a Craigslist 'Search'. Similar to the 'Ad' this is
        also lazy and follows the same layout with the `fetch()` and `to_dict()`
        methods.
        """
        self.query = query
        self.city = city
        self.category = category
        self.url = build_url(self.query, self.city, self.category)
        self.ads: List[Ad] = []

    def fetch(self, sort_by: Optional[str] = None, **kwargs) -> int:
        final_url = self.url
        if sort_by:
            final_url += f"&sort={sort_by}"
        self.request = requests.get(final_url, **kwargs)
        if self.request.status_code == 200:
            parser = SearchParser(self.request.content)
            self.ads = parser.ads
        return self.request.status_code

    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "city": self.city,
            "category": self.category,
            "url": self.url,
            "ads": [ad.to_dict() for ad in self.ads],
        }


def fetch_search(query: str, city: str, category: str = "sss", **kwargs) -> Search:
    """Functional implementation of a Craigslist search."""
    search = Search(query=query, city=city, category=category)
    search.fetch(**kwargs)
    return search


class SearchParser:
    def __init__(self, content: Union[str, bytes], **kwargs) -> None:
        self.soup = BeautifulSoup(content, "html.parser", **kwargs)

    @property
    def ads(self) -> List[Ad]:
        ads: List[Ad] = []
        for ad_html in self.soup.find_all("li", class_="cl-static-search-result"):
            if not isinstance(ad_html, Tag):
                continue  # Skip if not a Tag object

            try:
                a_tag = ad_html.find("a")
                if a_tag is None:
                    continue  # Skip if no 'a' tag is found

                url = a_tag["href"]
                title = ad_html.find(class_="title").text
                price_element = ad_html.find(class_="price")
                price = format_price(price_element.text) if price_element else None
                d_pid_match = re.search(r"/(\d+)\.html", url)
                d_pid = int(d_pid_match.group(1)) if d_pid_match else None

                ads.append(
                    Ad(url=url, title=title, price=price, d_pid=d_pid)
                )
            except (AttributeError, TypeError, KeyError, ValueError) as e:
                print(f"Error parsing ad: {e}")
                continue

        return ads
