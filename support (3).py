from aiogram import Router
from aiogram.types import Message

from database.db import get_referrals_count


router = Router()



@router.message(
    lambda message: message.text == "🎁 Рефералы"
)
async def referrals(message: Message):


    print("РЕФЕРАЛЫ НАЖАТЫ")


    user_id = message.from_user.id



    count = get_referrals_count(
        user_id
    )



    bot = await message.bot.get_me()



    link = (
        f"https://t.me/{bot.username}?start={user_id}"
    )



    await message.answer(

        "🎁 Реферальная система Prime Play\n\n"

        f"👥 Приглашено друзей: {count}\n\n"

        "💰 За каждого друга вы получаете 20₽\n\n"

        "🔗 Ваша уникальная ссылка:\n"

        f"{link}"

    )