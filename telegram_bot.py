import telebot

from databasework import Database
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton



TOKEN = 'TOKEN'

bot = telebot.TeleBot(TOKEN)

name = str
surname = str
biography = str
id = int
review = str


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = 'Привет, я бот, в котором вы можете найти знакомых людей,' \
    'добавить своих людей, посмотреть отзывы, ну и просто поугарать\n' \
    'Для просмотра команд используйте команду /help'
    bot.send_message(message.chat.id, text=welcome_text)


@bot.message_handler(commands=['help'])
def show_commands(message):
    commands_= "/addperson - добавить человека в базу\n" \
    "/viewpersons - посмотреть людей в базе\n" \
    "/selectperson - выбрать человека в базе"
    bot.send_message(message.chat.id, text=commands_)


@bot.message_handler(commands=['addperson']) # Adding a person to the databaase
def get_name(message):
    bot.send_message(message.chat.id, 'Введите имя человека')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message: Message) -> None:
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Введите фамилию человека')
    bot.register_next_step_handler(message, get_biography)

def get_biography(message: Message) -> None:
    global surname
    surname = message.text
    bot.send_message(
        message.chat.id, 
        'Расскажите что-нибудь об этом человеке,\nкто он такой, где учится или работает, например'
    )
    bot.register_next_step_handler(message, add_person)

def add_person(message: Message) -> None:
    global biography, name, surname
    biography = message.text
    db = Database()
    db.add_person(name, surname, biography)
    bot.send_message(message.chat.id, 'Успешно записан в базу!')
    name, surname, biography = '', '', ''


@bot.message_handler(commands=['viewpersons']) #Viewing people in the database
def view_persons_base(message):
    db = Database()
    people = db.view_people()
    bot.send_message(message.chat.id, 'База:\n' + str(people))


@bot.message_handler(commands=['selectperson']) #Select a person to view
def get_id(message):
    bot.send_message(message.chat.id, 'Введите id человека')
    bot.register_next_step_handler(message, select_person)

def select_person(message: Message) -> None:
    global id
    try:
        id = int(message.text)
    except ValueError:
        bot.reply_to(message, "Цифру введи, олень")
        id = 0
    else:
        markup = InlineKeyboardMarkup()
        button_1 = InlineKeyboardButton('Отзывы', callback_data='reviews')
        button_2 = InlineKeyboardButton('Оставить отзыв', callback_data='leave review')
        markup.add(button_1, button_2)

        db = Database()
        person = db.select_person(id)

        if person:
            person = person[0]
            bot.send_message(
                message.chat.id,
                f"ID: {person['id']}\n{person['first_name']}\n" \
                f"{person['surname']}\n\n{person['biography']}",
                reply_markup=markup
            )
        else:
            bot.reply_to(message, "Человека с таким id в базе нет")
            id = 0
            

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global id
    if call.message:

        if call.data == 'reviews': # Viewing the reviews about a person
            db = Database()
            reviews = db.view_reviews(id)
            if reviews:
                count = 0
                text = ''
                for i in reviews:
                    count += 1
                    text += f"{count}.\n{i.get('review')}\n\n"
                bot.send_message(call.message.chat.id, text)
            else:
                bot.send_message(call.message.chat.id, "Нет отзывов")

        elif call.data == 'leave review': # Adding a review about person to the database
            bot.send_message(call.message.chat.id, 'Напишите отзыв')
            bot.register_next_step_handler(call.message, add_review)

def add_review(message: Message) -> None:
    global review, id
    review = message.text
    db = Database()
    db.add_review(review, id)
    bot.send_message(message.chat.id, 'Отзыв успешно добавлен')
    id = 0



bot.infinity_polling()

