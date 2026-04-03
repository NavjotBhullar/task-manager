import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.settings import BASE_URL, PRICE_LIMIT
from utils.helpers import clean_price, get_rating
from db.database import books_collection
from datetime import datetime


BASE_SITE = "http://books.toscrape.com/"


def fetch_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except:
        return None
    return None


# 🔹 Extract detailed book info from product page
def extract_book_details(product_url):
    html = fetch_page(product_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # description
    desc_tag = soup.find("div", id="product_description")
    description = ""
    if desc_tag:
        description = desc_tag.find_next_sibling("p").text.strip()

    # category
    category = soup.find("ul", class_="breadcrumb").find_all("li")[2].text.strip()

    # availability
    availability = soup.find("p", class_="instock availability").text.strip()

    # image
    image_rel = soup.find("div", class_="item active").img["src"]
    image_url = urljoin(BASE_SITE, image_rel)

    price_text = soup.find("p", class_="price_color").text.strip()
    price = clean_price(price_text)

    return {
        "description": description,
        "category": category,
        "availability": availability,
        "image_url": image_url,
        "price":price
    }


# 🔹 Extract from listing page
def parse_listing(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []

    items = soup.find_all("article", class_="product_pod")

    for item in items:
        title = item.h3.a["title"]
        price_text = item.find("p", class_="price_color").text
        rating_class = item.find("p")["class"]

        # product link
        relative_url = item.h3.a["href"]
        product_url = urljoin(BASE_SITE + "catalogue/", relative_url)

        
        rating = get_rating(rating_class)


        # 🔥 fetch detailed page
        details = extract_book_details(product_url)

        # slug from URL
        slug = product_url.split("/")[-2]

        books.append({
            "title": title,
            "rating": rating,
            "product_url": product_url,
            "slug": slug,
            "created_at": datetime.utcnow(), 
            **details
        })

    return books


def scrape_books(pages: int):
    all_books = []

    page = 1
    while page <= pages:
        print(f"Scraping page {page}...")
        url = BASE_URL.format(page)

        html = fetch_page(url)
        if html:
            data = parse_listing(html)
            all_books.extend(data)

        page += 1

    # limit to 1000
    all_books = all_books[:1000]

    if all_books:
        books_collection.delete_many({})
        books_collection.insert_many(all_books, ordered=False)

    return len(all_books)