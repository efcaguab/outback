# Buying our new car with machine learning

**Why?** 

Me and my partner are on the hunt for a new (second hand) car. We know we want a Subaru Outback, have a budget and a range of age and mileage we're happy with.
But, even with our criteria, there are still hundreds of options available. It takes a lot of time to check them all and it is hard to know if a particular car is good value. 
So what's the solution? I nerd the it out over a couple days. I scrape data from the internet and building a machine learning model to find the best deals.

**What?**

So I wrote a couple of scripts. The first one, scrapes data from TradeMe, the largest car classified site in New Zealand, and stores the information in a local database. The second script, takes the data from the database and builds a simple regression that estimates a car value given the car's year and its mileage. 
That means spend less time looking at hundreds of classifieds as we focus only on those whose price is below the expectation. That also means we can be confident we got a good price (provided everything is OK with the car...)

**How?** 

I used *python* for this project. Why? Bevause 90% of the code I write is in R and it's nice to have some variety. 

*Scraping*:

There are three steps involved in scraping data:

1. Get the HTML code of the page. Because TradeMe is a dynamic website (which for our purpose means the HTML with the information we care about is only rendered from a browser) I use [*selenium*](https://www.selenium.dev/documentation/webdriver/), a web driver that gives me a conection to a browser that can be controlled programatically using python bindings. 
2. Extract the data from the HTML code. I use [*Beautiful Soup*](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to extract the contents of a particular HTML tag. 
3. Save the data. I use a very simple [*SQLite*](https://www.sqlite.org/index.html) database to store the data. I use a database because it's slightly easier to modify than a plain CSV file, but that would have worked well too. To create and update the database I use [*sqlalchemy*](https://www.sqlalchemy.org). There are probably easier pacakages but I wanted to get familiar with this one a try as is widely used in web applications.

So how do I apply those steps in this particular case? 

1. Figure out the URLs of the search results by scraping data from the first page of results. There might be hundreds of classifieds, so there might be dozens of pages with search results. 
2. Figure out the URLS of individual classsifieds by scraping data from all the pages with search resutls. 
3. Scrape the data from infividual classifeds. 
