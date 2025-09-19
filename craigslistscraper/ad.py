from bs4 import BeautifulSoup, Tag
import requests
import re
from typing import Optional, Union, List, Dict

from .utils import format_price


class Ad:
    def __init__(
        self,
        url: str,
        price: Optional[float] = None,
        title: Optional[str] = None,
        d_pid: Optional[int] = None,
        description: Optional[str] = None,
        attributes: Optional[Dict] = None,
        image_urls: Optional[List[str]] = None,
    ) -> None:
        """An abstraction for a Craigslist 'Ad'. At the bare minimum you need a
        url to define an ad. Although, at search-time, information such as the
        price, title, and d_pid can additionally be computed. If not provided,
        these are computed lazily if the user fetches the ad information with
        `ad.fetch()`.
        """
        self.url = url
        self.price = price
        self.title = title
        self.d_pid = d_pid
        self.description = description
        self.attributes = attributes
        self.image_urls = image_urls

    def __repr__(self) -> str:
        if self.title is None or self.price is None:
            return f"< {self.url} >"
        return f"< {self.title} (${self.price}): {self.url} >"

    def fetch(self, **kwargs) -> int:
        """Fetch additional data from the url of the ad."""
        self.request = requests.get(self.url, **kwargs)
        if self.request.status_code == 200:
            parser = AdParser(self.request.content)
            self.price = parser.price
            self.title = parser.title
            self.d_pid = parser.d_pid
            self.description = parser.description
            self.attributes = parser.attributes
            self.image_urls = parser.image_urls
            #self.metadata = parser.metadata  # Commented out as metadata is not used

        return self.request.status_code

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "price": self.price,
            "title": self.title,
            "d_pid": self.d_pid,
            "description": self.description,
            "image_urls": self.image_urls,
            "attributes": self.attributes,
        }


def fetch_ad(url: str, **kwargs) -> Ad:
    """Functional way to fetch the ad information given a url."""
    ad = Ad(url=url)
    ad.fetch(**kwargs)
    return ad


class AdParser:
    def __init__(self, content: Union[str, bytes], **kwargs) -> None:
        self.soup = BeautifulSoup(content, "html.parser", **kwargs)

        # Remove QR text. This is important when parsing the description.
        for qr in self.soup.find_all("p", class_="print-qrcode-label"):
            qr.decompose()

    @property
    def url(self) -> Optional[str]:
        meta_og_url = self.soup.find("meta", property="og:url")
        return meta_og_url.get("content") if meta_og_url else None

    @property
    def price(self) -> Optional[float]:
        element = self.soup.find("span", class_="price")
        return format_price(element.text) if element else None

    @property
    def title(self) -> Optional[str]:
        title_element = self.soup.find("span", id="titletextonly")
        return title_element.text if title_element else None

    @property
    def d_pid(self) -> Optional[int]:
        match = re.search(r"/(\d+)\.html", self.url or "")  # Handle potential NoneType
        try:
            return int(match.group(1)) if match else None
        except (AttributeError, TypeError):
            return None

    @property
    def description(self) -> Optional[str]:
        description_element = self.soup.find("section", id="postingbody")
        return description_element.text if description_element else None

    @property
    def attributes(self) -> Dict:
        attrs: Dict = {}
        for attr_group in self.soup.find_all("p", class_="attrgroup"):
            if not isinstance(attr_group, Tag):
                continue

            for attr in attr_group.find_all("span"):
                if not isinstance(attr, Tag):
                    continue
                kv = attr.text.split(": ")
                if len(kv) == 2:
                    attrs[kv[0]] = kv[1]
        return attrs

    @property
    def image_urls(self) -> List[str]:
        image_urls = []
        image_elements = self.soup.find_all("a", class_="thumb")
        if image_elements:
            for img_link in image_elements:
                img_url = img_link.get("href")
                if img_url:
                    image_urls.append(img_url)
            return image_urls

        # Fallback for pages with a single image and no thumbnails
        img_tag = self.soup.find("img")
        if img_tag and isinstance(img_tag, Tag) and "src" in img_tag.attrs:
            return [img_tag["src"]]
        
        return []
