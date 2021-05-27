import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
APCA_API_BASE_URL = "https://paper-api.alpaca.markets/v2"


def create_url():
    return APCA_API_BASE_URL + '/orders'


def create_headers():
    headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
    return headers


def create_data(ticker, side, notional, buy_target, take_profit, stop_loss):
    qty = float(notional) // float(buy_target)
    data = {
        "symbol": ticker,
        "side": side,
        "type": 'market',
        "qty": qty,
        "time_in_force": 'day',
        "order_class": 'bracket',
        "take_profit": {
            "limit_price": take_profit
        },
        "stop_loss": {
            "stop_price": stop_loss,
            "limit_price": stop_loss,
        }
    }

    return json.dumps(data)


def connect_to_endpoint(url, headers, data):
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def submit_order(ticker, side, notional, buy_target, take_profit, stop_loss):
    print("Buying ~${} of {} at {}, with take profit {} and stop loss {}".format(
        notional, ticker, buy_target, take_profit, stop_loss))
    url = create_url()
    headers = create_headers()
    data = create_data(ticker, side, notional,
                       buy_target, take_profit, stop_loss)
    json_response = connect_to_endpoint(url, headers, data)
    return json_response
