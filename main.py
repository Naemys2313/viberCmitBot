import json
import logging
import os

from viberbot import Api
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.message import Message

from flask import Flask, request, Response

START_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": "Reply message",
        "Text": "Push me!"
    }]
}

START_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": "Reply message",
        "Text": "Push me!"
    }]
}

REPLIES_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": "Replies message",
        "Text": "Replies message!"
    },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": "Back",
            "Text": "Back!"
        }]
}

bot_configuration = BotConfiguration(
    name="CmitUgraBot",
    avatar="",
    auth_token="4a94130713a7d0bb-3633cc6c70d45392-94364c0dd093822"
)

viber = Api(bot_configuration)

app = Flask(__name__)

logger = logging.getLogger()


def get_message(message: Message):
    messages = []
    tracking_data = message.tracking_data
    text = message.text
    if text == "Back":
        if tracking_data == "Reply message":
            messages.append(KeyboardMessage(tracking_data=text, keyboard=START_KEYBOARD))
    elif text == "Reply message" or text == "Replies message":
        messages.append(KeyboardMessage(tracking_data=text, keyboard=REPLIES_KEYBOARD))
    else:
        messages.append(KeyboardMessage(tracking_data=text, keyboard=START_KEYBOARD))
    messages.append(TextMessage(text))
    return messages


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("Recieve request. Post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        print("message.tracking_data: {0}, message.action_body{1}".format(viber_request.message.tracking_data,
                                                                          viber_request.message.text))
        message = get_message(viber_request.message)
        # lets echo back
        viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [TextMessage("Спасибо за подписку!")])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("Client failed receiving message. Failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
