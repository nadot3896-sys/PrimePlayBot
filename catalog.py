from aiogram import Router
from aiogram.types import Message

from database.games import get_games
from keyboards.games import games_keyboard


router = Router()


@router.message(lambda message: message.text == "🎮 Каталог игр")
async def catalog_handler(message: Message):

    games = get_games()


    if not games:

        await message.answer(
            "🎮 Каталог игр пока пуст."
        )

        return


    text = "🎮 Каталог игр:\n\n"


    for game in games:

        text += (
            f"🎮 {game[1]}\n\n"

            f"📅 1 день — {game[2]}₽\n"
            f"📅 3 дня — {game[3]}₽\n"
            f"📅 7 дней — {game[4]}₽\n\n"

            f"📌 {game[5]}\n\n"
        )


    await message.answer(
        text,
        reply_markup=games_keyboard(games)
    )