from selenium import webdriver
import chromedriver_binary
from bs4 import BeautifulSoup
import re 
from math import ceil
import time
import random

def get_results_urls(main_soup, search_url):
    result_cards = main_soup.find_all("div", class_ = "tm-motors-search-card__wrapper")
    n_cards_per_page = len(result_cards)
    n_listings_text = main_soup.find("h3", class_="tm-search-header-result-count__heading").get_text()
    n_listings = int(re.search("[0-9]+", n_listings_text).group())
    n_pages = ceil(n_listings / n_cards_per_page)
    return [search_url + "&page=" + str(i + 1) for i in range(n_pages)]

def get_listing_ids(results_page_soup, base_url):
    listing_links = results_page_soup.find_all("a", class_ = "tm-motors-search-card__link")
    listing_ids = [re.search("[0-9]+", link.get('href')).group() for link in listing_links]
    return listing_ids

def get_listing_urls(listing_ids, base_url):
    return [base_url + "listing/" + listing_id for listing_id in listing_ids]

def get_listing_kilometers(listing_soup):
    text = listing_soup.find("div", class_ = "tm-motors-vehicle-attributes__tag--content").get_text(strip = True)
    return int(re.search("[0-9]*,[0-9]+", text).group().replace(",", ""))

def get_listing_year(listing_soup):
    text = listing_soup.find("h1").get_text(strip = True)
    return int(re.search("^[0-9]{4}", text).group())

def get_listing_city(listing_soup):
    text = listing_soup.find("span", class_ = "tm-motors-date-city-watchlist__location").get_text(strip = True)
    return re.sub("^.+located in ", "", text).strip()

def scrape_results_url(search_results_url, base_url):
    print("Scraping ", search_results_url)
    time.sleep(random.randint(1, 3))
    driver = webdriver.Chrome()
    driver.get(search_results_url)
    result_soup = BeautifulSoup(driver.page_source)
    time.sleep(random.randint(1, 3))
    driver.close()
    return get_listing_urls(result_soup, base_url)

base_url = "https://www.trademe.co.nz/a/motors/cars/subaru/outback/"
search_url = base_url + "search?sort_order=motorslatestlistings"
driver = webdriver.Chrome()
driver.get(search_url)
results_main = BeautifulSoup(driver.page_source)
driver.close()

results_urls = get_results_urls(results_main, search_url)
listing_urls = []
for this_url in results_urls[0:2]:
    listing_urls = listing_urls + scrape_results_url(this_url, base_url)