from aiogram import Router, F
import asyncio

from aiogram.types import (
    CallbackQuery,
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database.db import change_balance


router = Router()


# =========================
# Кнопки выбора суммы
# =========================

def payment_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="⭐ 100",
                    callback_data="pay_100"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⭐ 500",
                    callback_data="pay_500"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⭐ 1000",
                    callback_data="pay_1000"
                )
            ]

        ]
    )



# =========================
# Кнопка ожидания
# =========================

def wait_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="⏳ Подождите 10 секунд...",
                    callback_data="wait"
                )
            ]

        ]
    )



# =========================
# Кнопка подтверждения
# =========================

def confirm_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✅ Подтверждаю",
                    callback_data="confirm_balance"
                )
            ]

        ]
    )



# =========================
# Защита перед пополнением
# =========================


@router.callback_query(
    lambda call: call.data == "add_balance"
)
async def add_balance_warning(
    call: CallbackQuery
):

    await call.message.edit_text(

        "⚠️ Внимание!\n\n"

        "Перед пополнением баланса будьте внимательны, "
        "что вы указали верную сумму и вы точно уверены, "
        "что хотите пополнить ваш баланс в боте.\n\n"

        "Это диалоговое окно сделано специально, "
        "чтобы обезопасить вас и ваши деньги "
        "от незапланированных трат.\n\n"

        "Если вы всё прочитали и подтверждаете "
        "пополнение баланса — нажмите кнопку ниже.\n\n"

        "⏳ Кнопка подтверждения появится через 10 секунд.",

        reply_markup=wait_keyboard()

    )


    await call.answer()


    await asyncio.sleep(10)


    await call.message.edit_reply_markup(

        reply_markup=confirm_keyboard()

    )



# =========================
# Нажатие во время ожидания
# =========================


@router.callback_query(
    lambda call: call.data == "wait"
)
async def wait_button(
    call: CallbackQuery
):

    await call.answer(

        "⏳ Подождите, кнопка появится автоматически",

        show_alert=True

    )



# =========================
# Подтверждение пополнения
# =========================


@router.callback_query(
    lambda call: call.data == "confirm_balance"
)
async def confirm_balance(
    call: CallbackQuery
):

    await call.message.answer(

        "💳 Выберите сумму пополнения:",

        reply_markup=payment_keyboard()

    )


    await call.answer()



# =========================
# Создание оплаты
# =========================


@router.callback_query(
    lambda call: call.data.startswith("pay_")
)
async def create_payment(
    call: CallbackQuery
):

    amount = int(
        call.data.replace(
            "pay_",
            ""
        )
    )


    await call.message.answer_invoice(

        title="Пополнение баланса Prime Play",

        description=f"Пополнение баланса на {amount}₽",

        payload=f"balance_{amount}",

        currency="XTR",

        prices=[

            LabeledPrice(
                label=f"{amount}₽",
                amount=amount
            )

        ]

    )


    await call.answer()



# =========================
# Проверка оплаты
# =========================


@router.pre_checkout_query()
async def pre_checkout(
    query: PreCheckoutQuery
):

    await query.answer(
        ok=True
    )



# =========================
# Успешная оплата
# =========================


@router.message(
    F.successful_payment
)
async def successful_payment(
    message: Message
):

    payment = message.successful_payment


    if payment.invoice_payload.startswith(
        "balance_"
    ):


        amount = int(
            payment.invoice_payload.replace(
                "balance_",
                ""
            )
        )


        change_balance(

            message.from_user.id,

            amount

        )


        await message.answer(

            "✅ Оплата прошла успешно!\n\n"

            f"💳 Вам начислено: +{amount}₽\n\n"

            "Спасибо за пополнение Prime Play 🎮"

        )