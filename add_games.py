# Импортируем кнопки Telegram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_ID


# Создаем клавиатуру главного меню
menu = ReplyKeyboardMarkup(
    
    keyboard=[

        # Первый ряд кнопок
        [
            KeyboardButton(
                text="🎮 Каталог игр"
            ),
            KeyboardButton(
                text="👤 Кабинет"
            )
        ],


        # Второй ряд кнопок
        [
            KeyboardButton(
                text="💳 Баланс"
            ),
            KeyboardButton(
    text="🎁 Рефералы"
            )
        ],


        # Третий ряд кнопок
        [
            KeyboardButton(
                text="📞 Поддержка"
            )
        ]

    ],


    # Делает кнопки красивыми,
    # чтобы они растягивались под экран
    resize_keyboard=True
)
def admin_menu_button(user_id):

    if user_id == ADMIN_ID:

        return ReplyKeyboardMarkup(
            keyboard=[

                [
                    KeyboardButton(
                        text="🎮 Каталог игр"
                    ),
                    KeyboardButton(
                        text="👤 Кабинет"
                    )
                ],

                [
                    KeyboardButton(
                        text="💳 Баланс"
                    ),
                    KeyboardButton(
                        text="🎁 Рефералы"
                    )
                ],

                [
                    KeyboardButton(
                        text="📞 Поддержка"
                    )
                ],

                [
                    KeyboardButton(
                        text="👑 Админ панель"
                    )
                ]

            ],
            resize_keyboard=True
        )


    return menu