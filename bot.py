from time import sleep
import datetime
from dotenv import load_dotenv
from twitter import getTimeline
from alpaca import submit_order

load_dotenv()

start_time = datetime.datetime.utcnow().replace(
    hour=15, minute=30, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")

ids = []


def updateStartTime():
    # global required to tell python to
    # update the variable start_time
    global start_time
    start_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def analyse(s):
    if "now buying: " not in s.lower():
        return

    s = s.split(" ")

    ticker = s[2][1:].strip()
    buy_target = float(s[4].split("\n")[0][2:].strip())
    sell_target = float(s[6][1:].strip())
    stop_loss = float(s[11].split("\n")[0][1:].strip())

    submit_order(ticker, 'buy', 1000.0, buy_target, sell_target, stop_loss)


def checkTweets():
    try:
        timeline = getTimeline(start_time)
        count = timeline["meta"]["result_count"]
        if count != 0:
            print("{} Trade Alert/s received".format(count))
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
    isOpen = datetime.datetime.utcnow().time() >= datetime.time(13, 30, 0)
    if(not isOpen):
        marketOpen = datetime.datetime.utcnow().replace(hour=13, minute=30, second=0)
        timeToOpen = marketOpen - datetime.datetime.utcnow()
        print("time until market open: {}".format(timeToOpen))
        print("Sleeping until market open...")
        sleep(timeToOpen.total_seconds())


def isMarketClosed():
    return datetime.datetime.utcnow().time() >= datetime.time(20, 0, 0)


def main():
    # marketClosed = False
    awaitMarketOpen()

    print("Market now open")

    while True:
        checkTweets()
        updateStartTime()
        sleep(5.0)

        if isMarketClosed():
            print("Market is closed.")
            # marketClosed = True
            break

    print("Exiting...")

    # if marketClosed:
    #     ids = []
    #     return main()


if __name__ == "__main__":
    main()
