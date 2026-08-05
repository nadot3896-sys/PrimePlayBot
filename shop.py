from aiogram import Router

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

import asyncio


from database.games import get_game

from database.db import (
    get_balance,
    update_balance,
    get_user_discount,
    get_free_account,
    take_account
)

from database.rentals import (
    add_rental,
    has_rental
)


router = Router()



# =========================
# Кнопки подтверждения
# =========================

def confirm_keyboard(waiting=True):

    if waiting:

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏳ Подождите 5 секунд",
                        callback_data="wait_buy"
                    )
                ]
            ]
        )


    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтверждаю",
                    callback_data="confirm_buy"
                )
            ]
        ]
    )



# =========================
# Покупка игры
# =========================

@router.callback_query(
    lambda call: call.data.startswith("buy_")
)
async def buy_game(call: CallbackQuery):


    data = call.data.split("_")


    game_id = int(data[1])

    days = int(data[2])


    game = get_game(game_id)


    if not game:

        await call.answer(
            "❌ Игра не найдена",
            show_alert=True
        )

        return



    telegram_id = call.from_user.id



    if has_rental(
        telegram_id,
        game_id
    ):

        await call.answer(
            "⚠️ Эта игра уже арендована",
            show_alert=True
        )

        return



    # =========================
    # Цена
    # =========================

    if days == 1:

        price = game[2]


    elif days == 3:

        price = game[3]


    elif days == 7:

        price = game[4]


    else:

        await call.answer(
            "❌ Ошибка срока",
            show_alert=True
        )

        return



    # =========================
    # Скидка
    # =========================

    discount = get_user_discount(
        telegram_id
    )


    if discount > 0:

        price = round(
            price - (price * discount / 100),
            2
        )



    await call.message.edit_text(

        "⚠️ Вы уверены?\n\n"

        f"🎮 Игра: {game[1]}\n"

        f"📅 Срок: {days} дней\n"

        f"💰 Стоимость: {price}₽\n\n"

        "Нажмите кнопку подтверждения.",

        reply_markup=confirm_keyboard(True)

    )



    if not hasattr(call.bot, "pending_buy"):

        call.bot.pending_buy = {}



    call.bot.pending_buy[telegram_id] = {


        "game_id": game_id,

        "days": days,

        "price": price,

        "game_name": game[1]

    }



    await call.answer()



    await asyncio.sleep(5)



    await call.message.edit_reply_markup(

        reply_markup=confirm_keyboard(False)

    )




# =========================
# Ожидание
# =========================

@router.callback_query(
    lambda call: call.data == "wait_buy"
)
async def wait_buy(call: CallbackQuery):


    await call.answer(
        "⏳ Подождите завершения защиты",
        show_alert=True
    )




# =========================
# Подтверждение покупки
# =========================

@router.callback_query(
    lambda call: call.data == "confirm_buy"
)
async def confirm_buy(call: CallbackQuery):


    telegram_id = call.from_user.id



    if not hasattr(call.bot, "pending_buy"):

        await call.answer(
            "❌ Покупка устарела",
            show_alert=True
        )

        return



    if telegram_id not in call.bot.pending_buy:


        await call.answer(
            "❌ Покупка устарела",
            show_alert=True
        )

        return



    data = call.bot.pending_buy[telegram_id]


    price = data["price"]



    # =========================
    # Проверка свободного аккаунта
    # =========================

    account = get_free_account(
        data["game_id"]
    )


    if not account:


        await call.answer(
            "❌ Сейчас нет свободных аккаунтов для этой игры.\n\n"
            "Попробуйте позже.",
            show_alert=True
        )


        del call.bot.pending_buy[telegram_id]


        return



    # =========================
    # Проверка баланса
    # =========================

    balance = get_balance(
        telegram_id
    )



    if balance < price:


        await call.answer(
            "❌ Недостаточно средств",
            show_alert=True
        )

        return



    # =========================
    # Списание денег
    # =========================

    new_balance = round(
        balance - price,
        2
    )


    update_balance(
        telegram_id,
        new_balance
    )



    # =========================
    # Выдача аккаунта
    # =========================

    account_id = account[0]

    login = account[1]

    password = account[2]



    take_account(
        account_id
    )



    account_text = (

        "\n\n🔐 Данные аккаунта:\n\n"

        f"👤 Логин: {login}\n"

        f"🔑 Пароль: {password}\n"

    )



    # =========================
    # Создание аренды
    # =========================

    add_rental(

        telegram_id,

        data["game_id"],

        data["days"],

        price,

        account_id

    )



    # =========================
    # Удаляем ожидание покупки
    # =========================

    del call.bot.pending_buy[telegram_id]



    await call.message.edit_text(


        "✅ Аренда успешно оформлена!\n\n"

        f"🎮 Игра: {data['game_name']}\n"

        f"📅 Срок: {data['days']} дней\n"

        f"💰 Оплачено: {price}₽\n"

        f"💳 Остаток: {new_balance}₽"

        f"{account_text}"

    )


    await call.answer()