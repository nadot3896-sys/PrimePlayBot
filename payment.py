from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



payment_menu = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="💳 Пополнить Баланс",
                callback_data="add_balance"
            )
        ]

    ]
)