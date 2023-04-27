from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types.message import Message
from states import States
import sqlite3


bot = Bot(token='6242052520:AAHeAksmvtXr2GF8VGCKZStrcvnqy-lrFg0')
dp = Dispatcher(bot,storage=MemoryStorage())

conn = sqlite3.connect('db.db', check_same_thread=False)
cursor = conn.cursor()



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет👋\nЧтобы узнать список команд - введите /commands")

@dp.message_handler(commands=['commands', 'help'])
async def help(message: types.Message):
    await message.answer("Список команд:")

    inline_keyboard = types.InlineKeyboardMarkup()

    buttons = [
        types.InlineKeyboardButton(text="/select", callback_data="select"),
        types.InlineKeyboardButton(text="/insert", callback_data="insert"),
        types.InlineKeyboardButton(text="/info", callback_data="info"),
    ]

    inline_keyboard.add(*buttons)
    await message.answer("Выберите действие:", reply_markup=inline_keyboard)

@dp.callback_query_handler(text="select")
async def select(call: types.CallbackQuery):
    inline_keyboard = types.InlineKeyboardMarkup()

    buttons = [
        types.InlineKeyboardButton(text="Вывести список товаров", callback_data="select_goods"),
        types.InlineKeyboardButton(text="Вывести список пользователей", callback_data="select_users"),
    ]

    inline_keyboard.add(*buttons)
    await call.message.answer("Выберите действие:", reply_markup=inline_keyboard)

@dp.callback_query_handler(text="select_goods")
async def select_goods(call: types.CallbackQuery):
    cursor.execute("SELECT * FROM goods")
    rows = cursor.fetchall()

    result = ''

    for row in rows:
        result += f'ID Товара: {row[0]}\nТовар: {row[1]}\nОписание: {row[2]}\nЦена: {row[3]}\n\n'
    await bot.send_message(call.message.chat.id, result)
    await call.message.answer("Попробуйте другие функции:\n"
                              "/commands")


@dp.callback_query_handler(text="select_users")
async def select_users(call: types.CallbackQuery):
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    result = ''

    for row in rows:
        result += f'ID Пользователя: {row[0]}\nЛогин: {row[1]}\nВозраст: {row[2]}\n\n'
    await bot.send_message(call.message.chat.id, result)
    await call.message.answer("Попробуйте другие функции:\n"
                              "/commands")


@dp.callback_query_handler(text="insert")
async def select(call: types.CallbackQuery):
    inline_keyboard = types.InlineKeyboardMarkup()

    buttons = [
        types.InlineKeyboardButton(text="Добавить новый товар", callback_data="insert_goods"),
        types.InlineKeyboardButton(text="Добавить нового пользователя", callback_data="insert_users")
    ]

    inline_keyboard.add(*buttons)
    await call.message.answer("Выберите действие:", reply_markup=inline_keyboard)


@dp.callback_query_handler(text="insert_goods")
async def insert_goods(call: types.CallbackQuery):
    await call.message.answer("Введите данные о товаре:\nНазвание товара:")
    await States.get_title.set()

@dp.message_handler(state=States.get_title)
async def get_title(message: Message, state: FSMContext):
    title = message.text
    await state.update_data(
        {
            'title': title,
        }
    )
    await message.answer('Описание товара:')
    await States.next()

@dp.message_handler(state=States.get_description)
async def get_description(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(
        {
            'description': description,
        }
    )
    await message.answer('Цену товара:')
    await States.next()

@dp.message_handler(state=States.get_price)
async def get_price(message: Message, state: FSMContext):
    price = message.text
    await state.update_data(
        {
            'price': price,
        }
    )
    data = await state.get_data()
    cursor.execute(f"INSERT INTO goods (title, description, price) VALUES('{data['title']}', '{data['description']}', '{data['price']}')")
    conn.commit()
    await message.answer(f'Успешно!✅\nДобавлен новый товар: {data["title"]}️\nОписание: {data["description"]}\nЦена: {data["price"]}')
    await message.answer("Попробуйте другие функции:\n"
                         "/commands")
    await state.finish()





@dp.callback_query_handler(text="insert_users")
async def insert_goods(call: types.CallbackQuery):
    await call.message.answer("Введите данные о пользователе:\nЛогин пользователя:")
    await States.get_username.set()

@dp.message_handler(state=States.get_username)
async def get_username(message: Message, state: FSMContext):
    username = message.text
    await state.update_data(
        {
            'username': username,
        }
    )
    await message.answer('Возраст пользователя:')
    await States.next()

@dp.message_handler(state=States.get_age)
async def get_age(message: Message, state: FSMContext):
    age = message.text
    await state.update_data(
        {
            'age': age,
        }
    )
    data = await state.get_data()
    cursor.execute(
        f"INSERT INTO users (username, age) VALUES('{data['username']}', '{data['age']}')")
    conn.commit()
    await message.answer(
        f'Успешно!✅\nДобавлен новый пользователь: {data["username"]}\nВозраст: {data["age"]}')
    await message.answer("Попробуйте другие функции:\n"
                         "/commands")
    await state.finish()






@dp.callback_query_handler(text="info")
async def info(call: types.CallbackQuery):
    await call.message.answer("Описание команд:\n/select - Выборка данных из базы\n/insert - Добавление данных в базу")
    await call.message.answer("Попробуйте другие функции:\n"
                         "/commands")


executor.start_polling(dp, skip_updates=True)
conn.close()
