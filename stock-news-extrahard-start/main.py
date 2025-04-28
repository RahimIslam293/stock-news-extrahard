import requests
import dotenv
import os
import datetime as dt

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

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
    return [1,2]


def should_send(yesterprice:float, daybefrprice:float) -> bool:
    differential = abs((daybefrprice - yesterprice) / daybefrprice)
    if differential > .05:
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
print(extracted_daily_stocks)

today = dt.datetime.today().date() # today's date
today_str = str(today)
offset = weekend_offset_calc()
yesterdays_date = today - dt.timedelta(days=offset[0]) #yesterdays date
yester_str = str(yesterdays_date)
day_before_yesterdays_date = yesterdays_date - dt.timedelta(days=offset[1]) #daybeforeyesterday
day_bef_yester_str = str(day_before_yesterdays_date)

yday_close = float(extract_close_price(stocks_dict=extracted_daily_stocks, date=yester_str))
day_bfre_yest_close = float(extract_close_price(stocks_dict=extracted_daily_stocks, date=day_bef_yester_str))

to_send = should_send(yday_close,day_bfre_yest_close)

if to_send:
    print("Get News")



## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


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

