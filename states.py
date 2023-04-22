from aiogram.dispatcher.filters.state import State, StatesGroup

class States(StatesGroup):
    get_title = State()
    get_description = State()
    get_price = State()

    get_username = State()
    get_age = State()
