import logging
import os
from threading import Thread

from viberbot import Api
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.message import Message
from viberbot.api.messages.url_message import URLMessage

from flask import Flask, request, Response

import schedule
import time

user_ids = []

KEY_CALLBACK = "action_type"
KEY_TEXT = "text"

BACK = {
    KEY_CALLBACK: "back",
    KEY_TEXT: "Назад"
}

DAY_OF_WEAK = [
    {KEY_CALLBACK: "monday",
     KEY_TEXT: "Понедельник"},
    {KEY_CALLBACK: "tuesday",
     KEY_TEXT: "Вторник"},
    {KEY_CALLBACK: "wednesday",
     KEY_TEXT: "Среда"},
    {KEY_CALLBACK: "thursday",
     KEY_TEXT: "Четверг"},
    {KEY_CALLBACK: "friday",
     KEY_TEXT: "Пятница"},
    {KEY_CALLBACK: "saturday",
     KEY_TEXT: "Суббота"},
    {KEY_CALLBACK: "sunday",
     KEY_TEXT: "Воскресенье"},
]

TIMETABLE = {KEY_CALLBACK: "timetable",
             KEY_TEXT: "Расписание"}

NEWS = {KEY_CALLBACK: "news",
        KEY_TEXT: "Новости ЦМИТ"}

PAY = {KEY_CALLBACK: "pay_late",
       KEY_TEXT: 'Оплатить'}

COURSES = {KEY_CALLBACK: "courses",
           KEY_TEXT: 'Курсы'}

COURSE_3D_MODELING = {KEY_CALLBACK: "3d_modeling",
                      KEY_TEXT: '3D моделирование'}
COURSE_MULTIMEDIA = {KEY_CALLBACK: "multimedia",
                     KEY_TEXT: 'Мультимедиа'}
COURSE_PROGRAMMING = {KEY_CALLBACK: "programming",
                      KEY_TEXT: 'Программирование'}
COURSE_GRAPHIC_DESIGN = {KEY_CALLBACK: "graphic_design",
                         KEY_TEXT: 'Графический дизайн'}
COURSE_UAV = {KEY_CALLBACK: "uav",
              KEY_TEXT: 'БПЛА'}
COURSE_ALGORITHMIC = {KEY_CALLBACK: "algorithmic",
                      KEY_TEXT: 'Алгоритмика'}

SIGN_UP_FOR_COURSE = {KEY_CALLBACK: "sign_up_for_course",
                      KEY_TEXT: 'Записаться на курс'}


def get_timetable_buttons():
    buttons = []
    for day_of_weak in DAY_OF_WEAK:
        if day_of_weak.get(KEY_CALLBACK) == DAY_OF_WEAK[6].get(KEY_CALLBACK):
            break
        buttons.append({
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": day_of_weak.get(KEY_CALLBACK),
            "Text": day_of_weak.get(KEY_TEXT)
        })

    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": DAY_OF_WEAK[6].get(KEY_CALLBACK),
        "Text": DAY_OF_WEAK[6].get(KEY_TEXT)
    })

    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": BACK.get(KEY_CALLBACK),
        "Text": BACK.get(KEY_TEXT)
    })

    return buttons


START_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": TIMETABLE.get(KEY_CALLBACK),
        "Text": TIMETABLE.get(KEY_TEXT)
    },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": NEWS.get(KEY_CALLBACK),
            "Text": NEWS.get(KEY_TEXT)
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": PAY.get(KEY_CALLBACK),
            "Text": PAY.get(KEY_TEXT)
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSES.get(KEY_CALLBACK),
            "Text": COURSES.get(KEY_TEXT)
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": SIGN_UP_FOR_COURSE.get(KEY_CALLBACK),
            "Text": SIGN_UP_FOR_COURSE.get(KEY_TEXT)
        }
    ]
}

TIMETABLE_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": get_timetable_buttons()
}

COURSES_KEYBOARD = {
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#FFFFFF",
        "ActionType": "reply",
        "ActionBody": COURSE_3D_MODELING.get(KEY_CALLBACK),
        "Text": COURSE_3D_MODELING.get(KEY_TEXT)
    },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSE_MULTIMEDIA.get(KEY_CALLBACK),
            "Text": COURSE_MULTIMEDIA.get(KEY_TEXT)
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSE_PROGRAMMING.get(KEY_CALLBACK),
            "Text": COURSE_PROGRAMMING.get(KEY_TEXT)
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSE_GRAPHIC_DESIGN.get(KEY_CALLBACK),
            "Text": COURSE_GRAPHIC_DESIGN.get(KEY_TEXT)
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSE_UAV.get(KEY_CALLBACK),
            "Text": COURSE_UAV.get(KEY_TEXT)
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#FFFFFF",
            "ActionType": "reply",
            "ActionBody": COURSE_ALGORITHMIC.get(KEY_CALLBACK),
            "Text": COURSE_ALGORITHMIC.get(KEY_TEXT)
        },

    ]
}

bot_configuration = BotConfiguration(
    name="CmitUgraBot",
    avatar="",
    auth_token="4a94130713a7d0bb-3633cc6c70d45392-94364c0dd093822"
)

viber = Api(bot_configuration)

app = Flask(__name__)

logger = logging.getLogger()

HELLO_MESSAGE = "Вас приветствует цифровой помощник ЦМИТа Вертикаль.\nДля начала взаимодействия нажмите кнопку начать"


def get_messages(message: Message):
    text = message.text
    if text == TIMETABLE.get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = None
    elif text == NEWS.get(KEY_CALLBACK):
        keyboard = START_KEYBOARD
        reply_message = NEWS.get(KEY_TEXT)
    elif text == PAY.get(KEY_CALLBACK):
        keyboard = START_KEYBOARD
        reply_message = 'Юридический адрес: 628452, АО Ханты-Мансийский Автономный округ- Югра, район Сургутский, ' \
                        'поселок солнечный, улица Дорожная, дом 7, литера а, офис 21\n' \
                        'Дата регистрации: 14 июня 2018 года\n\n' \
                        'ОГРН: 1188617008788\n' \
                        'ИНН/КПП: 8617035294/861701001\n' \
                        'Кор.счет: 30101810800000000651\n' \
                        'Западно-Сибирский банк ПАО «Сбербанк» г.Тюмень\n' \
                        'БИК: 047102651\n' \
                        'ИНН: 7707083893\n' \
                        'КПП: 860202001\n' \
                        'ОГРН: 1027700132195\n' \
                        'ОКВЭД: 74.14, 33.10, 25.13\n' \
                        'ОКПО: 02816697\n' \
                        'Расчетный счет: 40702810267170005394\n\n' \
                        'Генеральный директор: Тарасович Павел Юрьевич'

    elif text == DAY_OF_WEAK[0].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[0].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[1].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[1].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[2].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[2].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[3].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[3].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[4].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[4].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[5].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[5].get(KEY_TEXT)
    elif text == DAY_OF_WEAK[6].get(KEY_CALLBACK):
        keyboard = TIMETABLE_KEYBOARD
        reply_message = DAY_OF_WEAK[6].get(KEY_TEXT)
    elif text == BACK.get(KEY_CALLBACK):
        keyboard = START_KEYBOARD
        reply_message = None

    else:
        keyboard = START_KEYBOARD
        reply_message = HELLO_MESSAGE

    if reply_message is None:
        return [KeyboardMessage(keyboard=keyboard)]
    else:
        return [TextMessage(text=reply_message, keyboard=keyboard)]


def mailing():
    for user_id in user_ids:
        viber.send_messages(user_id, [TextMessage(keyboard=START_KEYBOARD, text="Тест авторассылки")])


schedule.every().day.at("10:30").do(mailing)


def schedule_mailing():
    while True:
        schedule.run_pending()
        time.sleep(1)


thread = Thread(target=schedule_mailing)
thread.start()


@app.route('/', methods=['POST'])
def incoming():
    print(thread.is_alive())
    logger.debug("Recieve request. Post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        print("message.tracking_data: {0}, message.action_body{1}".format(viber_request.message.tracking_data,
                                                                          viber_request.message.text))
        if viber_request.sender.id not in user_ids:
            user_ids.append(viber_request.sender.id)

        viber.send_messages(viber_request.sender.id, get_messages(viber_request.message))
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [TextMessage(text=HELLO_MESSAGE, keyboard=START_KEYBOARD)])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("Client failed receiving message. Failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
