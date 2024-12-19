from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from bs4 import BeautifulSoup
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

MostFollowed_scraped_stocks = []
MostFollowed_status = []

Prominent_Stocks = []
Prominent_Stocks_price = []
def get_Info():
    """
    Function to scrape news from BBC and update the global headlines and subtext lists.
    """
    global MostFollowed_scraped_stocks, MostFollowed_status, Prominent_Stocks, Prominent_Stocks_price
    try:
        # Fetch and parse the HTML
        html_text = requests.get('https://www.google.com/finance/?hl=en').text
        soup = BeautifulSoup(html_text, 'lxml')
        ##---
        stocks = soup.find_all('div', class_ = 'c7mied')
        stocks_status = soup.find_all('div', class_= 'O7j0Wc')
        ##---
        Stocks_Prominent = soup.find_all('div', class_ = 'sR5uIb D4uc1d')
        for stock in Stocks_Prominent:
            Prominent_Stocks_price.append(stock.find('div', class_='s1OkXb').text.strip())

        for stock in stocks:
            MostFollowed_scraped_stocks.append(stock.text.strip())

        for stock in stocks_status:
            MostFollowed_status.append(stock.text.strip())

        for stock in Stocks_Prominent: 
            Prominent_Stocks.append(stock.text.strip())

    except Exception as e:
        print(f"Error occurred during scraping: {e}")

@app.route('/stock', methods=['GET'])
def get_news():
    """
    API endpoint to fetch the latest scraped news and other reads.
    """
    MostFollowed_ReponseObject = [
        {   
            "ProminentStocks": [{
                "Stock": StockName,
                "Price": StockPrice, 
            }for StockName, StockPrice in zip(Prominent_Stocks,Prominent_Stocks_price)],
            "Most-followed": [{
                "company": MostFollowed,
                "StockStatus": MostStatus
            } for MostFollowed,MostStatus in zip(MostFollowed_scraped_stocks,MostFollowed_status)]
        }
    ]

    return jsonify(MostFollowed_ReponseObject)


if __name__ == '__main__':
    # Scheduler setup
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_Info, 'interval', minutes=10)  # Run every 10 minutes
    scheduler.start()

    # Run the first scrape immediately
    get_Info()

    # Start the Flask app
    try:
        app.run(debug=True, host='0.0.0.0', port=10000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()