import requests
from bs4 import BeautifulSoup
import sqlite3
import csv
from datetime import date

class ArticleScraper:
    def __init__(self):
        self.base_url = "https://www.theverge.com/#content"
        self.article_urls = []
        self.article_data = []

    def fetch_article_urls(self):
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.text, "html.parser")
            articles_container = soup.find('div', "h-full w-full lg:max-h-full lg:w-[380px] lg:pt-[174px]")
            if articles_container is not None:
                articles_list = articles_container.find("ol")
                for article in articles_list:
                    url = article.find("a")["href"]
                    self.article_urls.append(f"https://www.theverge.com{url}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching article URLs: {e}")

    def scrape_articles(self):
        if len(self.article_urls) > 0:
            article_id = 0
            for url in self.article_urls:
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    article_heading = soup.find('h1')
                    
                    # extract article title
                    title = article_heading.text.strip()

                    # extract author(s)
                    authors_list = soup.find('div').find('p')
                    authors = ""
                    for author in authors_list:
                        authors = authors.strip() + " " + author.text.strip()

                    # extract date
                    date_raw = soup.find('time').text.strip().split(",")
                    date_str = date_raw[0] + date_raw[1]

                    # create a tuple object of each article                
                    article_id = article_id + 1
                    article = (article_id, url, title, authors, date_str)
                    self.article_data.append(article)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred while scraping article data for {url}: {e}")
        else:
            print("No article URLs found.")

    def save_to_csv(self):
        filename = date.today().strftime("%d%m%Y") + "_articles.csv"
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                csvwriter = csv.writer(f)
                csvwriter.writerow(["id", "url", "title", "author(s)", "date"])
                for article in self.article_data:
                    csvwriter.writerow(article)

        except IOError as e:
            print(f"An error occurred while saving to CSV: {e}")

    def save_to_sqlite(self):
        try:
            conn = sqlite3.connect("articles.db")
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    authors TEXT,
                    date TEXT
                )
                """
            )
            for article in self.article_data:
                c.execute("INSERT OR IGNORE INTO articles (url, title, authors, date) VALUES (?, ?, ?, ?)",
                      (article[1], article[2], article[3], article[4]))
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"An error occurred while saving to SQLite: {e}")

if __name__ == "__main__":
    scraper = ArticleScraper()
    scraper.fetch_article_urls()
    scraper.scrape_articles()
    scraper.save_to_csv()
    scraper.save_to_sqlite()