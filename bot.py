import os
from pytwitter import Api
from time import sleep
import datetime
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.environ['BEARER_TOKEN']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
api = Api(bearer_token=BEARER_TOKEN)
stockTweetsAccountID = "1388217130709962753"
start_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

ids = []


def updateStartTime():
    start_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def getTimeline():
    response = api.get_timelines(
        user_id=stockTweetsAccountID, return_json=True, start_time=start_time)
    updateStartTime()
    return response


def analyse(s):
    if "Now buying: " not in s:
        return

    s = s.split(" ")

    ticker = s[2][1:].strip()
    buy_target = s[4].split("\n")[0][2:].strip()
    sell_target = s[6][1:].strip()
    stop_loss = s[14].split("\n")[0][1:].strip()

    # submitOrder('TSLA', 'buy', '1', '1000.0', '69.69')
    submitOrder(ticker, 'buy', '1000', sell_target, stop_loss)


def checkTweets():
    try:
        timeline = getTimeline()
        if timeline["meta"]["result_count"] != 0:
            for tweet in timeline["data"]:
                id = tweet["id"]
                text = tweet["text"]

                if id not in ids:
                    ids.append(id)

                    analyse(text)
    except Exception as e:
        print("Error: %s" % e)
    finally:
        return


# Wait for market to open.
def awaitMarketOpen():
    isOpen = alpaca.get_clock().is_open
    if(not isOpen):
        clock = alpaca.get_clock()
        openingTime = clock.next_open.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        timeToOpen = (openingTime - currTime)
        print(str(timeToOpen / 60) + " minutes until market open.")
        print("Sleeping until market open...")
        sleep(timeToOpen)


# Submit an order if quantity is above 0.
def submitOrder(ticker, side, notional, take_profit, stop_loss):
    if(int(notional) > 0):
        try:
            alpaca.submit_order(
                symbol=ticker,
                side=side,
                type='market',
                notional=notional,
                time_in_force='day',
                order_class='bracket',
                take_profit=dict(
                    limit_price=take_profit,
                ),
                stop_loss=dict(
                    stop_price=stop_loss,
                    limit_price=stop_loss,
                )
            )
            print("Market order of | " + notional + " " +
                  ticker + " " + side + " | completed.")
        except Exception as e:
            print("Error: {}".format(e))
            print("Order of | " + notional + " " + ticker +
                  " " + side + " | did not go through.")
    else:
        print("Quantity is 0, order of | " + notional +
              " " + ticker + " " + side + " | not completed.")


def marketClosedTime():
    clock = alpaca.get_clock()
    closingTime = clock.next_close.replace(
        tzinfo=datetime.timezone.utc).timestamp()

    return closingTime


def isMarkedClosed():
    # return closingTime <= datetime.datetime.utcnow().timestamp()
    return datetime.datetime.now().time() >= datetime.time(21, 0, 0)


def main():
    # marketClosed = False
    awaitMarketOpen()

    print("Market now open")

    updateStartTime()

    # closingTime = marketClosedTime()

    while True:
        checkTweets()
        sleep(2.0)

        if isMarkedClosed():
            print("Market is closed.")
            # marketClosed = True
            break

    # if marketClosed:
    #     ids = []
    #     return main()


if __name__ == "__main__":
    main()
