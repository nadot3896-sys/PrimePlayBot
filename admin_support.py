from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from config import ADMIN_ID
from database.db import connect
from aiogram.filters import StateFilter


router = Router()



class AnswerTicket(StatesGroup):

    message = State()



# =========================
# Список обращений
# =========================


@router.callback_query(
    lambda call: call.data == "support_tickets"
)
async def tickets(call: CallbackQuery):


    if call.from_user.id != ADMIN_ID:
        return



    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id,user_id,message,status
        FROM tickets
        ORDER BY id DESC
        """
    )


    tickets = cursor.fetchall()


    connection.close()



    if not tickets:

        await call.message.answer(
            "📩 Обращений пока нет"
        )

        await call.answer()
        return




    buttons = []


    text = "📩 Обращения:\n\n"



    for ticket in tickets[:20]:


        text += (
            f"🎫 #{ticket[0]}\n"
            f"👤 ID: {ticket[1]}\n"
            f"📌 {ticket[3]}\n\n"
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🎫 Открыть #{ticket[0]}",
                    callback_data=f"ticket_{ticket[0]}"
                )
            ]
        )



    await call.message.answer(

        text,

        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )

    )


    await call.answer()






# =========================
# Открыть тикет
# =========================


@router.callback_query(
    lambda call: call.data.startswith("ticket_")
)
async def open_ticket(call: CallbackQuery):


    ticket_id = int(
        call.data.replace(
            "ticket_",
            ""
        )
    )



    connection = connect()
    cursor = connection.cursor()



    cursor.execute(
        """
        SELECT user_id,message,status
        FROM tickets
        WHERE id=?
        """,
        (
            ticket_id,
        )
    )



    ticket = cursor.fetchone()


    connection.close()



    if not ticket:

        await call.answer(
            "Тикет не найден",
            show_alert=True
        )

        return




    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="✍️ Ответить",

                    callback_data=f"answer_{ticket_id}"

                )

            ]

        ]

    )




    await call.message.answer(

        f"🎫 Тикет #{ticket_id}\n\n"

        f"👤 Пользователь: {ticket[0]}\n\n"

        f"💬 Сообщение:\n{ticket[1]}\n\n"

        f"📌 Статус: {ticket[2]}",

        reply_markup=keyboard

    )



    await call.answer()






# =========================
# Нажата кнопка ответить
# =========================


@router.callback_query(

    lambda call: call.data.startswith("answer_")

)
async def answer_button(

        call: CallbackQuery,

        state:FSMContext

):


    ticket_id = int(

        call.data.replace(
            "answer_",
            ""
        )

    )


    await state.update_data(

        ticket_id=ticket_id

    )


    await call.message.answer(

        "✍️ Напишите ответ пользователю:"

    )



    await state.set_state(

        AnswerTicket.message

    )



    await call.answer()





# =========================
# Отправка ответа
# =========================


@router.message(
    StateFilter(AnswerTicket.message)
)
async def send_answer(

        message: Message,

        state:FSMContext

):


    if message.from_user.id != ADMIN_ID:

        return



    data = await state.get_data()


    ticket_id = data["ticket_id"]




    connection = connect()

    cursor = connection.cursor()



    cursor.execute(

        """
        SELECT user_id

        FROM tickets

        WHERE id=?

        """,

        (
            ticket_id,
        )

    )


    user = cursor.fetchone()




    if user:



        await message.bot.send_message(

            user[0],

            "📩 Ответ поддержки:\n\n"

            + message.text

        )



        cursor.execute(

            """
            UPDATE tickets

            SET 

            status='Закрыт',

            answer=?

            WHERE id=?

            """,

            (

                message.text,

                ticket_id

            )

        )



    connection.commit()

    connection.close()



    await message.answer(

        "✅ Ответ отправлен пользователю"

    )


    await state.clear()