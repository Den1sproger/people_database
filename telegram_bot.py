import os

import telebot

from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv, find_dotenv
from databasework import Database


load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)

name: str
biography: str
id: int
review: str


WELCOME_TEXT = 'Привет, я бот, в котором вы можете найти знакомых людей,' \
    'добавить своих людей, посмотреть отзывы, ну и просто поугарать\n' \
    'Для просмотра инструкции используйте команду /help'

INSTRUCTION = """
<em>Кнопка</em> <b>Добавить в базу</b> - добавить чела в базу
<em>Кнопка</em> <b>Посмотреть кто есть</b> - посмотреть людей в базе
<em>Кнопка</em> <b>Выбрать человека</b> - выбрать человека в базе,
чтобы посмотреть отзывы или оставить отзыв.
<em>Чтобы выбрать, надо будет ввести id, это левая циферка в списке людей.</em>

Если вы начали какую-либо операцию, но потом передумали
добавлять отзыв/чела, нажмите кнопку <b>cancel</b>
"""


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Добавить в базу'), KeyboardButton('Посмотреть кто есть'))
    kb.add(KeyboardButton('Выбрать человека'), KeyboardButton('cancel'))
    return kb


def get_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        keyboard=[
            [InlineKeyboardButton('Отзывы', callback_data='reviews')],
            [InlineKeyboardButton('Оставить отзыв', callback_data='leave review')]
        ]
    )
    return ikb


def check_cancel(func):
    def decorator(message: types.Message) -> None:
        if message.text == 'cancel':
            bot.send_message(message.chat.id, 'Операция прервана')
        else:
            func(message)
    return decorator



@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id, text=WELCOME_TEXT, reply_markup=get_kb())



@bot.message_handler(commands=['help'])
def show_commands(message: types.Message):
    bot.send_message(message.chat.id, text=INSTRUCTION, parse_mode='HTML')



@bot.message_handler(func=lambda message: message.text == 'Добавить в базу') # Adding a person to the databaase
def get_name(message: types.Message) -> None:
    bot.send_message(message.chat.id, 'Введите имя и фамилию человека')
    bot.register_next_step_handler(message, get_biography)


@check_cancel
def get_biography(message: Message) -> None:
    global name
    name = message.text
    bot.send_message(
        message.chat.id, 
        'Расскажите что-нибудь об этом человеке,\nкто он такой, где учится или работает, например'
    )
    bot.register_next_step_handler(message, add_person)


@check_cancel
def add_person(message: Message) -> None:
    global biography, name
    biography = message.text
    db = Database()
    db.add_person(name, biography)
    bot.send_message(message.chat.id, 'Успешно записан в базу!')
    name, biography = '', ''



@bot.message_handler(func=lambda message: message.text == 'Посмотреть кто есть') # Viewing people in the database
def view_persons_base(message: types.Message) -> None:
    db = Database()
    people = db.view_people()
    bot.send_message(message.chat.id, 'База:\n' + str(people))



@bot.message_handler(func=lambda message: message.text == 'Выбрать человека') # Select a person to view
def get_id(message):
    bot.send_message(message.chat.id, 'Введите id человека')
    bot.register_next_step_handler(message, select_person)


@check_cancel
def select_person(message: types.Message) -> None:
    global id
    try:
        id = int(message.text)
    except ValueError:
        bot.reply_to(message, "Цифру введи, олень")
        bot.register_next_step_handler(message, select_person)
    else:
        db = Database()
        person = db.select_person(id)

        if person:
            person = person[0]
            bot.send_message(
                message.chat.id,
                f"ID: {person['id']}\n{person['surname']}\n\n{person['biography']}",
                reply_markup=get_ikb()
            )
        else:
            bot.reply_to(message, "Человека с таким id в базе нет")
            id = 0
            


@bot.callback_query_handler(func=lambda callback: callback.data == 'reviews')
def view_reviews(callback: types.CallbackQuery) -> None:
    # Viewing the reviews about a person
    db = Database()
    reviews = db.view_reviews(id)
    if reviews:
        count = 0
        text = ''
        for i in reviews:
            count += 1
            text += f"{count}.\n{i.get('review')}\n\n"
        bot.send_message(callback.message.chat.id, text)
    else:
        bot.send_message(callback.message.chat.id, "Нет отзывов")



@bot.callback_query_handler(func=lambda callback: callback.data == 'leave review')
def input_review(callback: types.CallbackQuery) -> None:
    bot.send_message(callback.message.chat.id, 'Напишите отзыв')
    bot.register_next_step_handler(callback.message, add_review)


@check_cancel
def add_review(message: types.Message) -> None:
    global review, id
    review = message.text
    db = Database()
    db.add_review(review, id)
    bot.send_message(message.chat.id, 'Отзыв успешно добавлен')
    review, id = '', 0



bot.infinity_polling()

