import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv, find_dotenv
from databasework import Database


load_dotenv(find_dotenv())
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

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
Если вы начали какую-либо операцию, но потом передумали
добавлять отзыв/чела, введите команду /cancel
"""


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton('Добавить в базу')],
                [KeyboardButton('Посмотреть кто есть')],
                [KeyboardButton('Выбрать человека')]  
            ]
        )
    return kb


def get_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton('Отзывы', callback_data='reviews')],
            [InlineKeyboardButton('Оставить отзыв', callback_data='leave review')]
        ]
    )
    return ikb


class ProfileStatesGroup(StatesGroup):
    getting_name = State()
    getting_biography = State()
    getting_id = State()
    getting_review = State()


@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message,
                     state: FSMContext) -> None:
    if state is None: pass
    else:
        await state.finish()
        await message.reply('Вы прервали операцию')
                

@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=get_kb())


@dp.message_handler(commands=['help'])
async def help(message: types.Message) -> None:
    await message.answer(INSTRUCTION, parse_mode='HTML')


@dp.message_handler(Text(equals='Добавить в базу')) # Adding a person to the databaase
async def get_name(message: types.Message) -> None:
    await ProfileStatesGroup.getting_name.set()
    await message.answer('Введите имя и фамилию человека')


@dp.message_handler(state=ProfileStatesGroup.getting_name)
async def get_biography(message: types.Message,
                        state: FSMContext) -> None:
    global name
    async with state.proxy() as proxy:
        proxy['getting_name'] = message.text
        name = proxy['getting_name']
    await ProfileStatesGroup.getting_biography.set()
    await message.answer(
        'Расскажите что-нибудь об этом человеке,\nкто он такой, где учится или работает, например'
    )


@dp.message_handler(state=ProfileStatesGroup.getting_biography)
async def add_person(message: types.Message,
               state: FSMContext) -> None:
    global biography, name
    async with state.proxy() as proxy:
        proxy['getting_biography'] = message.text
        biography = proxy['getting_biography']
    db = Database()
    db.add_person(name, biography)
    name, biography = '', ''
    await state.finish()
    await message.answer('Успешно записан в базу!')


@dp.message_handler(Text(equals='Посмотреть кто есть')) # Viewing people in the database
async def view_persons_base(message: types.Message) -> None:
    db = Database()
    people = db.view_people()
    await message.answer('База:\n' + str(people))


@dp.message_handler(lambda message: not message.text.isdigit(), state=ProfileStatesGroup.getting_id)
async def check_id(message: types.Message) -> None:
    await message.reply("Цифру введи, олень")


@dp.message_handler(Text(equals='Выбрать человека')) # Select a person to view
async def get_id(message: types.Message) -> None:
    await ProfileStatesGroup.getting_id.set()
    await message.answer('Введите id человека')
    

@dp.message_handler(state=ProfileStatesGroup.getting_id)
async def select_person(message: types.Message,
                        state: FSMContext) -> None:
    global id
    async with state.proxy() as proxy:
        proxy['getting_id'] = message.text
        id = proxy['getting_id']
    id = int(message.text)
    db = Database()
    person = db.select_person(id)

    if person:
        person = person[0]
        await message.answer(
            f"ID: {person['id']}\n{person['surname']}\n\n" \
            f"{person['biography']}",
            reply_markup=get_ikb()
        )
    else:
        await message.reply("Человека с таким id в базе нет")
        id = 0
    await state.finish()
            

@dp.callback_query_handler(lambda callback: callback.data == 'reviews')
async def view_reviews(callback: types.CallbackQuery) -> None:
    global id
    db = Database()
    reviews = db.view_reviews(id)
    if reviews:
        count = 0
        text = ''
        for i in reviews:
            count += 1
            text += f"{count}.\n{i.get('review')}\n\n"
        await bot.send_message(callback.message.chat.id, text=text)
    else:
        await bot.send_message(callback.message.chat.id, "Нет отзывов")


@dp.callback_query_handler(lambda callback: callback.data == 'leave review')
async def get_review(callback: types.CallbackQuery) -> None:
    await ProfileStatesGroup.getting_review.set()
    await bot.send_message(callback.message.chat.id, 'Напишите отзыв')


@dp.message_handler(state=ProfileStatesGroup.getting_review)
async def add_review(message: types.Message,
                     state: FSMContext) -> None:
    global id, review
    async with state.proxy() as proxy:
        proxy['getting_review'] = message.text
        review = proxy['getting_review']
    db = Database()
    db.add_review(review, id)
    id, review = 0, ''
    await state.finish()
    await message.answer('Успешно записан в базу')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

