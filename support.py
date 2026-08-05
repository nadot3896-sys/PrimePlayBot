from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import create_ticket
from config import ADMIN_ID
from aiogram.filters import StateFilter


router = Router()


class Support(StatesGroup):

    message = State()



@router.message(
    lambda message: message.text == "📞 Поддержка"
)
async def support_start(
    message: Message,
    state: FSMContext
):

    print("КНОПКА ПОДДЕРЖКА НАЖАТА")

    await message.answer(
        "🆘 Опишите вашу проблему:"
    )

    await state.set_state(
        Support.message
    )



@router.message(
    StateFilter(Support.message)
)
async def support_send(
    message: Message,
    state: FSMContext
):

    create_ticket(
        message.from_user.id,
        message.from_user.username or "Нет username",
        message.text
    )
    await message.bot.send_message(
    ADMIN_ID,
    "📩 Новое обращение!\n\n"
    f"👤 Пользователь:\n"
    f"ID: {message.from_user.id}\n"
    f"Username: @{message.from_user.username or 'Нет username'}\n\n"
    f"💬 Проблема:\n"
    f"{message.text}\n\n"
    "➡️ Для ответа откройте раздел «📩 Обращения» в админ-панели."
)
    await message.answer(
        "✅ Ваше обращение создано!\n\n"
        "Ожидайте ответа поддержки."
    )

    await state.clear()
    