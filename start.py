from aiogram import Router

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    User
)

from database.db import (
    get_balance,
    get_level_progress,
    get_user_discount
)

from database.rentals import (
    get_rentals_count,
    get_user_rentals
)

from datetime import datetime


router = Router()



# =========================
# Полоса прогресса
# =========================

def progress_bar(percent):

    blocks = 10

    filled = int(
        blocks * percent / 100
    )

    return (
        "🟩" * filled +
        "⬜" * (blocks - filled)
    )



# =========================
# Создание кабинета
# =========================

async def show_profile(
        message,
        user: User
):

    username = (
        f"@{user.username}"
        if user.username
        else "Не указан"
    )


    telegram_id = user.id

    full_name = user.full_name


    balance = round(
        float(get_balance(telegram_id)),
        2
    )


    level_data = get_level_progress(
        telegram_id
    )


    level = level_data["level"]

    total_spent = level_data["spent"]

    left = level_data["left"]

    percent = level_data["percent"]


    discount = get_user_discount(
        telegram_id
    )


    bar = progress_bar(
        percent
    )


    rentals_count = get_rentals_count(
        telegram_id
    )


    rentals = get_user_rentals(
        telegram_id
    )



    text = (

        "👤 Твой личный кабинет\n\n"

        f"Имя: {full_name}\n"
        f"Username: {username}\n"
        f"ID: {telegram_id}\n\n"

        f"⭐ Уровень: {level}\n"
        f"🎁 Скидка: {discount}%\n\n"

        f"💳 Всего потрачено: {total_spent:.2f}₽\n\n"

        "📈 Прогресс уровня:\n"

        f"{bar}\n"

        f"Осталось: {left:.2f}₽\n\n"

        f"💰 Баланс: {balance:.2f} ₽\n"

        f"🎮 Аренд: {rentals_count}\n\n"

    )



    buttons = []



    if rentals:


        text += "🎮 Твои активные аренды:\n\n"



        for rental in rentals:


            rental_id = rental[0]

            game_name = rental[1]

            end_time = rental[4]



            try:


                end = datetime.strptime(
                    end_time,
                    "%Y-%m-%d %H:%M:%S"
                )


                remaining = (
                    end - datetime.now()
                )



                if remaining.total_seconds() > 0:


                    seconds = int(
                        remaining.total_seconds()
                    )


                    days = seconds // 86400


                    hours = (
                        seconds % 86400
                    ) // 3600


                    minutes = (
                        seconds % 3600
                    ) // 60



                    time_text = (
                        f"{days}д "
                        f"{hours}ч "
                        f"{minutes}м"
                    )


                else:

                    time_text = "Время вышло"



            except:


                time_text = "Ошибка времени"




            text += (

                f"🎮 Игра: {game_name}\n"

                f"💰 Итоговая сумма: {rental[3]}₽\n"

                f"⏳ Осталось: {time_text}\n\n"

            )



            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🔄 Продлить {game_name}",
                        callback_data=f"extend_{rental_id}"
                    )
                ]
            )



            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"❌ Отменить {game_name}",
                        callback_data=f"cancel_{rental_id}"
                    )
                ]
            )



    else:


        text += (
            "🎮 У тебя пока нет арендованных игр\n"
        )



    buttons.append(
        [
            InlineKeyboardButton(
                text="🔄 Обновить кабинет",
                callback_data="refresh_profile"
            )
        ]
    )



    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )



    await message.answer(
        text,
        reply_markup=keyboard
    )





# =========================
# Кнопка Кабинет
# =========================

@router.message(
    lambda message: message.text == "👤 Кабинет"
)

async def profile_button(message: Message):


    await show_profile(
        message,
        message.from_user
    )





# =========================
# Обновление кабинета
# =========================

@router.callback_query(
    lambda call: call.data == "refresh_profile"
)

async def refresh_profile(call: CallbackQuery):


    await call.message.delete()



    await show_profile(
        call.message,
        call.from_user
    )



    await call.answer()