# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-509502385906-508901040097-0LgWFzLvYpkmUpgbAqtLlH2o"
slack_client_id = "509502385906.509398738819"
slack_client_secret = "77e08abc01fd12ee43fb03885bf5aa57"
slack_verification = "c9RlB5fzLTyhRVYsN0hjRjGI"
sc = SlackClient(slack_token)

# ũ�Ѹ� �Լ� �����ϱ�
def _crawl_game_keywords(text):

        url = "https://play.google.com/store/apps/top/category/GAME"
        req = urllib.request.Request(url)

        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")

        #�Լ��� ������ �ּ���
        keywords = []
        for data in (soup.find_all("div", class_="card-content")):
            result = ''
            for d in data.find_all("a", class_="title"):
                result += d.get_text()
                result += '��(��) '
            for e in data.find_all("div", class_="tiny-star"):
                f = e.find("div")["style"]
                f = f.split()[1][:2]
                result += f + "���Դϴ�."
            keywords.append(result)

        # �ѱ� ������ ���� �տ� unicode u�� �����ش�.
        return u'\n'.join(keywords[:20])

# �̺�Ʈ �ڵ��ϴ� �Լ�
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_game_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
