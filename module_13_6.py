"""Создайте клавиатуру InlineKeyboardMarkup с 2 кнопками InlineKeyboardButton:
С текстом 'Рассчитать норму калорий' и callback_data='calories'
С текстом 'Формулы расчёта' и callback_data='formulas'
Создайте новую функцию main_menu(message), которая:
Будет обёрнута в декоратор message_handler, срабатывающий при передаче текста 'Рассчитать'.
Сама функция будет присылать ранее созданное Inline меню и текст 'Выберите опцию:'
Создайте новую функцию get_formulas(call), которая:
Будет обёрнута в декоратор callback_query_handler, который будет реагировать на текст 'formulas'.
Будет присылать сообщение с формулой Миффлина-Сан Жеора.
Измените функцию set_age и декоратор для неё:
Декоратор смените на callback_query_handler, который будет реагировать на текст 'calories'.
Теперь функция принимает не message, а call. Доступ к сообщению будет следующим - call.message.
По итогу получится следующий алгоритм:
Вводится команда /start
На эту команду присылается обычное меню: 'Рассчитать' и 'Информация'.
В ответ на кнопку 'Рассчитать' присылается Inline меню: 'Рассчитать норму калорий' и 'Формулы расчёта'
По Inline кнопке 'Формулы расчёта' присылается сообщение с формулой.
По Inline кнопке 'Рассчитать норму калорий' начинает работать машина состояний по цепочке."""

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

"""Инициализация клавиатуры"""
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text="Расcчитать")
button2 = KeyboardButton(text="Информация")
kb.add(button1, button2)

kbinline = InlineKeyboardMarkup(inline_keyboard=True)
bttn1 = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")
bttn2 = InlineKeyboardButton(text="Формулы расcчёта", callback_data="formula")
kbinline.add(bttn1, bttn2)

calc_menu = kbinline


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler()
async def hello_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message_handler(text="Информация")
async def show_info(message):
    await message.answer("""Этот бот расчситывает калории 
                            для приведения вас в хорошее состояние при средней актвности.""")


"""Подключаем InlineKeyboard"""


@dp.message_handler(text='Расcчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=calc_menu)


"""Вывод формулы по которой производится рассчет"""


@dp.callback_query_handler(text='formula')
async def get_formulas(callbutton):
    await callbutton.message.answer("для мужчин: (10 x вес (кг) + 6.25 x рост (см) – 5 x возраст (г) + 5) x 1.55")
    await callbutton.answer()


"""Запрос возраста"""


@dp.callback_query_handler(text='calories')
async def set_age(callbutton):
    await callbutton.message.answer("Укажите свой возраст.")
    await UserState.age.set()
    await callbutton.answer()


"""Запрос роста после получения возраста"""


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(agetxt=message.text)
    data = await state.get_data()
    await message.answer("Укажите свой рост.")
    await UserState.growth.set()


"""Запрос веса после получения роста"""


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growthtxt=message.text)
    data = await state.get_data()
    await message.answer("Укажите свой вес.")
    await UserState.weight.set()


"""Рассчет и вывод результата"""


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weighttxt=message.text)
    data = await state.get_data()
    calories = 10 * float(data['weighttxt']) + 6.25 * float(data['growthtxt']) - 5 * (float(data['agetxt']) + 5) * 1.55
    await message.answer(f"Ваша норма {calories} калорий.")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
