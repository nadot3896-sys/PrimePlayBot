from aiogram import Router
from aiogram.types import Message

from database.db import get_balance
from keyboards.payment import payment_menu


router = Router()


@router.message(lambda message: message.text == "💳 Баланс")
async def balance_handler(message: Message):

    balance = get_balance(message.from_user.id)

    await message.answer(
    f"💳 Ваш баланс: {balance}₽\n\n"
    "Чтобы пополнить баланс, нажмите кнопку ниже 👇",
    reply_markup=payment_menu
)