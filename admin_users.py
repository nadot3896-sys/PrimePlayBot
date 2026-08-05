from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import ADMIN_ID

from database.db import (
    get_all_users,
    change_balance,
    block_user
)


router = Router()



# =========================
# Список пользователей
# =========================

@router.callback_query(
    lambda call: call.data == "admin_users"
)
async def admin_users(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    users = get_all_users()


    if not users:

        await call.message.answer(
            "👥 Пользователей пока нет"
        )

        await call.answer()
        return



    for user in users[:20]:

        telegram_id = user[1]
        name = user[2]
        username = user[3]
        balance = user[4]


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[

                [
                    InlineKeyboardButton(
                        text="💰 +100₽",
                        callback_data=f"user_add100_{telegram_id}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="💰 +500₽",
                        callback_data=f"user_add500_{telegram_id}"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="🚫 Заблокировать",
                        callback_data=f"user_block_{telegram_id}"
                    )
                ]

            ]
        )


        await call.message.answer(

            "👤 Пользователь\n\n"
            f"Имя: {name}\n"
            f"Username: @{username if username else 'нет'}\n"
            f"ID: {telegram_id}\n"
            f"💰 Баланс: {balance}₽",

            reply_markup=keyboard
        )


    await call.answer()





# =========================
# +100 рублей
# =========================

@router.callback_query(
    lambda call: call.data.startswith("user_add100_")
)
async def add100(call: CallbackQuery):

    telegram_id = int(
        call.data.replace(
            "user_add100_",
            ""
        )
    )


    change_balance(
        telegram_id,
        100
    )


    await call.answer(
        "✅ Добавлено 100₽"
    )





# =========================
# +500 рублей
# =========================

@router.callback_query(
    lambda call: call.data.startswith("user_add500_")
)
async def add500(call: CallbackQuery):

    telegram_id = int(
        call.data.replace(
            "user_add500_",
            ""
        )
    )


    change_balance(
        telegram_id,
        500
    )


    await call.answer(
        "✅ Добавлено 500₽"
    )





# =========================
# Блокировка
# =========================

@router.callback_query(
    lambda call: call.data.startswith("user_block_")
)
async def block(call: CallbackQuery):

    telegram_id = int(
        call.data.replace(
            "user_block_",
            ""
        )
    )


    block_user(
        telegram_id
    )


    await call.answer(
        "🚫 Пользователь заблокирован"
    )