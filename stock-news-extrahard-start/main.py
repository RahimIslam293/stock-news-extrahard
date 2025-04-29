import requests
import dotenv
import os
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
stock_direction : str
differential : float
def extract_close_price(stocks_dict:dict, date:str) -> float:
    return stocks_dict[date]["4. close"]

def weekend_offset_calc() -> list:
    """"This function is specifically called to handle the weekend case.
    Markets on open on weekends, so we need a special offset. First value will be first offset (yesterday),
    second value will be second offset (Day before yesterday)"""
    td = str(dt.datetime.today().weekday())
    if td == "7":
        return [2,3]
    if td == "0":
        return [3,4]
    if td == "1":
        return [1,3]
    return [1,2]


def should_send(yesterprice:float, daybefrprice:float) -> bool:
    global stock_direction
    global differential
    differential = (yesterprice - daybefrprice)  / daybefrprice
    if differential > 0:
        stock_direction = "🔺"
    if differential < 0:
        stock_direction = "🔻"
    if abs(differential) > .05:
        return True
    return False



## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
dotenv.load_dotenv()
stock_url = "https://www.alphavantage.co/query"
stock_api_key = os.getenv("ALPHAVANTAGE_API_KEY")
time_series = "TIME_SERIES_DAILY"
stock_output_size = "compact"
stock_uri_params = {
    "function": time_series, # API Key
    "symbol": STOCK, #Stock Ticker
    "apikey": stock_api_key, # API Key
    "outputsize": stock_output_size #Output Size

}

resp = requests.get(stock_url, params=stock_uri_params) # API Call
resp.raise_for_status() #raise status if exception
full_stock_data = resp.json() #Pulled stock data
extracted_daily_stocks = full_stock_data["Time Series (Daily)"] # Extracted only stock data


today = dt.datetime.today().date() # today's date
today_str = str(today)
offset = weekend_offset_calc()
yesterdays_date = today - dt.timedelta(days=offset[0]) #yesterdays date
yester_str = str(yesterdays_date)
day_before_yesterdays_date = yesterdays_date - dt.timedelta(days=offset[1]) #daybeforeyesterday
day_bef_yester_str = str(day_before_yesterdays_date)

# yday_close = 200
# day_bfre_yest_close = 100
yday_close = float(extract_close_price(stocks_dict=extracted_daily_stocks, date=yester_str))
day_bfre_yest_close = float(extract_close_price(stocks_dict=extracted_daily_stocks, date=day_bef_yester_str))

to_send = should_send(yday_close,day_bfre_yest_close)
if to_send:
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

    news_url = "https://newsapi.org/v2/everything"
    news_api_key = os.getenv("NEWSAPI_ORG_API_KEY")
    # print(news_api_key)
    news_uri_params = {
        "q": COMPANY_NAME,
        "to": today_str,
        "apiKey": news_api_key,
        "pageSize": 3
    }
    resp = requests.get(news_url, params=news_uri_params)
    resp.raise_for_status()
    full_news_data = resp.json()
    extracted_news_data = full_news_data["articles"]
    differential *= 100
    message_to_send = f"{STOCK}: {stock_direction} {abs(differential)}% \n"

    for article in extracted_news_data:
        message_to_send += f"Headline: {article['title']} \n"
        message_to_send += f"Descriptions: {article['description']} \n\n"



## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

    account_sid = os.getenv("TWILIO_ACCOUNT_SID ")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid,auth_token)

    message = client.messages.create(
        body= message_to_send,
        from_="+18557722840",
        to="+19106830231",

    )
    print(message.body)


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

