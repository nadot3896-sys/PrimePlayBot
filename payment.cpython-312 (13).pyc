from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def games_keyboard(games):

    keyboard = []


    for game in games:

        game_id = game[0]

        name = game[1]

        price_1_day = game[2]
        price_3_days = game[3]
        price_7_days = game[4]


        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🎮 {name}",
                    callback_data="ignore"
                )
            ]
        )


        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📅 1 день — {price_1_day}₽",
                    callback_data=f"buy_{game_id}_1"
                )
            ]
        )


        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📅 3 дня — {price_3_days}₽",
                    callback_data=f"buy_{game_id}_3"
                )
            ]
        )


        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📅 7 дней — {price_7_days}₽",
                    callback_data=f"buy_{game_id}_7"
                )
            ]
        )


    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )