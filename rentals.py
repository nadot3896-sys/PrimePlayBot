from aiogram import Router
import asyncio

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database.db import (
    get_balance,
    update_balance,
    add_total_spent
)

from database.games import get_game

from database.rentals import (
    get_rental,
    extend_rental,
    cancel_rental
)


router = Router()



# ==================================
# ПРОДЛЕНИЕ АРЕНДЫ
# ==================================

@router.callback_query(
    lambda call: call.data.startswith("extend_")
    and not call.data.startswith("extend_days_")
    and not call.data.startswith("extend_confirm_")
)
async def extend_start(call: CallbackQuery):

    rental_id = int(
        call.data.replace(
            "extend_",
            ""
        )
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 1 день",
                    callback_data=f"extend_days_{rental_id}_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 3 дня",
                    callback_data=f"extend_days_{rental_id}_3"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 7 дней",
                    callback_data=f"extend_days_{rental_id}_7"
                )
            ]
        ]
    )


    await call.message.answer(
        "📅 Выберите срок продления:",
        reply_markup=keyboard
    )


    await call.answer()



# ==================================
# ЗАЩИТА ПРОДЛЕНИЯ 5 СЕКУНД
# ==================================

@router.callback_query(
    lambda call: call.data.startswith("extend_days_")
)
async def extend_days(call: CallbackQuery):

    data = call.data.split("_")


    rental_id = int(data[2])
    days = int(data[3])


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Подождите 5 секунд",
                    callback_data="wait"
                )
            ]
        ]
    )


    await call.message.edit_text(
        "⚠️ Подтверждение продления\n\n"
        "Вы действительно хотите продлить аренду?\n\n"
        "После подтверждения средства будут списаны с вашего баланса.",
        reply_markup=keyboard
    )


    await call.answer()


    await asyncio.sleep(5)


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтверждаю",
                    callback_data=f"extend_confirm_{rental_id}_{days}"
                )
            ]
        ]
    )


    await call.message.edit_reply_markup(
        reply_markup=keyboard
    )



# ==================================
# ПОДТВЕРЖДЕНИЕ ПРОДЛЕНИЯ
# ==================================

@router.callback_query(
    lambda call: call.data.startswith("extend_confirm_")
)
async def extend_confirm(call: CallbackQuery):

    data = call.data.split("_")


    rental_id = int(data[2])
    days = int(data[3])


    rental = get_rental(
        rental_id
    )


    if not rental:

        await call.answer(
            "❌ Аренда не найдена",
            show_alert=True
        )

        return



    telegram_id = rental[1]
    game_id = rental[2]


    game = get_game(
        game_id
    )


    if days == 1:

        price = game[2]

    elif days == 3:

        price = game[3]

    else:

        price = game[4]



    balance = get_balance(
        telegram_id
    )


    if balance < price:

        await call.answer(
            "❌ Недостаточно средств",
            show_alert=True
        )

        return



    update_balance(
        telegram_id,
        balance - price
    )


    extend_rental(
        rental_id,
        days,
        price
    )






    await call.message.answer(
        "✅ Аренда продлена!\n\n"
        f"📅 Добавлено: {days} дней\n"
        f"💰 Списано: {price}₽"
    )


    await call.answer()



# ==================================
# ОТМЕНА АРЕНДЫ
# ==================================

@router.callback_query(
    lambda call: call.data.startswith("cancel_")
    and not call.data.startswith("cancel_confirm_")
)
async def cancel_start(call: CallbackQuery):

    rental_id = int(
        call.data.replace(
            "cancel_",
            ""
        )
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Подождите 5 секунд",
                    callback_data="wait"
                )
            ]
        ]
    )


    await call.message.edit_text(
        "⚠️ Отмена аренды\n\n"
        "Вы уверены что хотите отменить аренду?\n\n"
        "После подтверждения аренда будет удалена.",
        reply_markup=keyboard
    )


    await call.answer()


    await asyncio.sleep(5)


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить отмену",
                    callback_data=f"cancel_confirm_{rental_id}"
                )
            ]
        ]
    )


    await call.message.edit_reply_markup(
        reply_markup=keyboard
    )



# ==================================
# ПОДТВЕРЖДЕНИЕ ОТМЕНЫ
# ==================================

@router.callback_query(
    lambda call: call.data.startswith("cancel_confirm_")
)
async def cancel_confirm(call: CallbackQuery):

    rental_id = int(
        call.data.replace(
            "cancel_confirm_",
            ""
        )
    )


    refund = cancel_rental(
        rental_id
    )


    if refund is None:

        await call.answer(
            "❌ Аренда не найдена",
            show_alert=True
        )

        return



    await call.message.answer(
        "❌ Аренда отменена\n\n"
        f"💰 Возвращено: {refund}₽"
    )


    await call.answer()