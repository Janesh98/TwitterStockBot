import requests
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.environ['BEARER_TOKEN']
stockTweetsAccountID = "1388217130709962753"


def create_url():
    return "https://api.twitter.com/2/users/{}/tweets".format(stockTweetsAccountID)


def get_params(start_time):
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "created_at", "start_time": start_time}


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def getTimeline(start_time):
    url = create_url()
    headers = create_headers(BEARER_TOKEN)
    params = get_params(start_time)
    json_response = connect_to_endpoint(url, headers, params)
    return json_response
