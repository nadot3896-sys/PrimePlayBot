from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.menu import admin_menu_button

from database.db import (
    add_user,
    user_exists,
    add_referral,
    has_referrer
)


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):

    telegram_id = message.from_user.id

    full_name = message.from_user.full_name

    username = message.from_user.username


    # проверяем есть ли пользователь

    user = user_exists(
        telegram_id
    )


    if user is None:


        # создаём пользователя

        add_user(
            telegram_id,
            full_name,
            username
        )


        text = (
            "👋 Добро пожаловать в Prime Play!\n\n"
            "Ты успешно зарегистрирован 🎮"
        )


        # проверяем реферальную ссылку

        args = message.text.split()


        if len(args) > 1:


            try:

                referrer_id = int(args[1])


            except:

                referrer_id = None



            if referrer_id:


                # нельзя пригласить самого себя

                if referrer_id != telegram_id:


                    # проверяем что у пользователя ещё нет пригласителя

                    if not has_referrer(telegram_id):


                        result = add_referral(
                            telegram_id,
                            referrer_id
                        )


                        if result:


                            try:

                                await message.bot.send_message(
                                    referrer_id,
                                    "🎁 Новый друг зарегистрировался!\n\n"
                                    "💰 Вам начислено 20₽"
                                )


                            except:

                                pass



    else:


        text = (
            "👋 С возвращением в Prime Play!\n\n"
            "Выбери нужный раздел:"
        )



    await message.answer(
    text,
    reply_markup=admin_menu_button(
        message.from_user.id
    )
)