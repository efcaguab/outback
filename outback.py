# %% Import required libraries
from selenium import webdriver
import chromedriver_binary
from bs4 import BeautifulSoup
import re 
from math import ceil
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone


# %% Set up a sqlite table to store the information
engine = create_engine('sqlite:///outback.db', echo = True)
Base = declarative_base()

class Listing(Base):
    __tablename__ = 'listing'
    listing_id = Column(Integer, primary_key=True)
    listing_url = Column(String)
    price_type = Column(String)
    kilometers = Column(Integer)
    year = Column(Integer)
    city = Column(String)
    price = Column(Integer)
    on_road_costs = Column(Boolean)
    scraped_on = Column(DateTime)

Base.metadata.create_all(engine)

# %%
# Selenium options
options = webdriver.ChromeOptions()
options.add_argument('headless')


# %%

def get_results_urls(main_soup, search_url):
    result_cards = main_soup.find_all("div", class_ = "tm-motors-search-card__wrapper")
    n_cards_per_page = len(result_cards)
    n_listings_text = main_soup.find("h3", class_="tm-search-header-result-count__heading").get_text()
    n_listings = int(re.search("[0-9]+", n_listings_text).group())
    n_pages = ceil(n_listings / n_cards_per_page)
    return [search_url + "&page=" + str(i + 1) for i in range(n_pages)]

def get_listing_ids(results_page_soup):
    listing_links = results_page_soup.find_all("a", class_ = "tm-motors-search-card__link")
    listing_ids = [re.search("[0-9]+", link.get('href')).group() for link in listing_links]
    return listing_ids

def get_listing_url(listing_id, base_url):
    return base_url + "listing/" + str(listing_id)

def get_listing_kilometers(listing_soup):
    text = listing_soup.find("div", class_ = "tm-motors-vehicle-attributes__tag--content").get_text(strip = True)
    return int(re.search("[0-9]*,?[0-9]+", text).group().replace(",", ""))

def get_listing_year(listing_soup):
    text = listing_soup.find("h1").get_text(strip = True)
    return int(re.search("^[0-9]{4}", text).group())

def get_listing_city(listing_soup):
    text = listing_soup.find("span", class_ = "tm-motors-date-city-watchlist__location").get_text(strip = True)
    return re.sub("^.+located in ", "", text).strip()

def get_price_type(listing_soup):
    element = listing_soup.find("div", class_ = "tm-motors-pricing-box__price-display")
    if element is not None:
        text = element.get_text(strip=True)
        if text == "Asking price":
            return "asking"
        elif text == "Or near offer":
            return "near_offer"
    else:
        buy_now_element = listing_soup.find("p", class_ = "tm-buy-now-box__price")
        if buy_now_element is not None:
            return "buy now"

def get_price(listing_soup):
    element = listing_soup.find("div", class_ = "tm-motors-pricing-box__price")
    if element is not None:
        text = element.get_text(strip=True)
    else:
        buy_now_element = listing_soup.find("p", class_ = "tm-buy-now-box__price")
        if buy_now_element is not None:
            text = buy_now_element.find("strong").get_text(strip=True)
        else: 
            return None
    return int(re.search("[0-9]*,?[0-9]+", text).group().replace(",", ""))

def get_orc(listing_soup):
    text = listing_soup.find("div", class_ = "tm-orc-description__container").div.get_text(strip=True)
    if text == "Includes on road costs":
        return True
    elif text == "Excludes on road costs":
        return False

def scrape_listing_ids(search_results_url):
    print("Scraping ", search_results_url)
    driver = webdriver.Chrome(options=options)
    driver.get(search_results_url)
    result_soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.close()
    return get_listing_ids(result_soup)

def get_listing_soup(listing_url):
    print("Scraping ", listing_url)
    driver = webdriver.Chrome(options=options)
    driver.get(listing_url)
    listing_soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.close()
    return listing_soup

def listing_exists(this_listing_id):
    this_query = session.query(Listing.listing_id).filter(Listing.listing_id == this_listing_id).exists()
    return session.query(this_query).scalar()

def listing_expired(listing_soup):
    element_404 = listing_soup.find("div", class_ = "status-code")
    if element_404 is not None:
        if element_404.get_text(strip=True) == "404":
            return True
    return False

def scrape_listing(this_listing_id):
    if not listing_exists(this_listing_id):
        this_url = get_listing_url(this_listing_id, base_url)
        listing_soup = get_listing_soup(this_url)
        if not listing_expired(listing_soup):
            this_listing_info = Listing(
                listing_id = this_listing_id, 
                listing_url = this_url, 
                price_type = get_price_type(listing_soup),
                kilometers = get_listing_kilometers(listing_soup), 
                year = get_listing_year(listing_soup), 
                city = get_listing_city(listing_soup), 
                price = get_price(listing_soup),
                on_road_costs = get_orc(listing_soup),
                scraped_on = datetime.now(timezone.utc))
            session.add(this_listing_info)
            session.commit()
        else:
            print("Listing expired")
    else:
        print("Listing", this_listing_id, "is already in the database", sep=" ")


# %%
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


# %%
base_url = "https://www.trademe.co.nz/a/motors/cars/subaru/outback/"
search_url = base_url + "search?sort_order=motorslatestlistings"
driver = webdriver.Chrome(options=options)
print("Scraping main result page")
driver.get(search_url)
results_main = BeautifulSoup(driver.page_source, features="html.parser")
driver.close()

results_urls = get_results_urls(results_main, search_url)
listing_ids = []
for this_url in results_urls:
    these_listing_ids = scrape_listing_ids(this_url)
    listing_ids = listing_ids + these_listing_ids
    if listing_exists(these_listing_ids[-1]):
        break


# %%
for this_id in reversed(listing_ids):
    scrape_listing(this_id)

# %% [markdown]
# this_listing_id = 3263840843
# this_url = get_listing_url(this_listing_id, base_url)
# listing_soup_asking = get_listing_soup(this_url)
# 
# this_listing_id = 3264216227
# this_url = get_listing_url(this_listing_id, base_url)
# listing_soup_nearoffer = get_listing_soup(this_url)
# 
# this_listing_id = 3257304680
# this_url = get_listing_url(this_listing_id, base_url)
# listing_soup_auction = get_listing_soup(this_url)
# 
# this_listing_id = 3242889738
# this_url = get_listing_url(this_listing_id, base_url)
# listing_soup_auction2 = get_listing_soup(this_url)

