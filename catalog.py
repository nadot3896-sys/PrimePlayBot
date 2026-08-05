from aiogram import Router

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.filters import StateFilter

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from config import ADMIN_ID


from keyboards.admin import (
    admin_menu,
    games_admin_menu
)


from database.games import (
    add_game,
    get_games,
    delete_game as delete_game_db,
    update_game_price
)


from database.rentals import (
    get_today_statistics
)


from database.db import (
    get_open_tickets,
    get_all_tickets,
    close_ticket,
    add_account,
    get_all_accounts,
    set_account_tech,
    delete_account,
    return_account_from_tech
)



router = Router()





# =========================
# FSM состояния
# =========================


class AddGame(StatesGroup):

    name = State()

    price_1_day = State()

    price_3_days = State()

    price_7_days = State()

    description = State()



class ChangePrice(StatesGroup):

    game_id = State()

    price_1_day = State()

    price_3_days = State()

    price_7_days = State()



class AddAccount(StatesGroup):

    game_id = State()

    login = State()

    password = State()



# =========================
# Проверка администратора
# =========================


def is_admin(user_id):

    return user_id == ADMIN_ID

# =========================
# Вход в админ панель
# =========================


@router.message(
    lambda message: message.text == "👑 Админ панель"
)
async def admin_button(message: Message):

    if not is_admin(message.from_user.id):
        return


    await message.answer(
        "👑 Админ панель\n\n"
        "Выберите действие:",
        reply_markup=admin_menu
    )





# =========================
# Команда /admin
# =========================


@router.message(
    lambda message: message.text == "/admin"
)
async def admin_command(message: Message):

    if not is_admin(message.from_user.id):

        await message.answer(
            "❌ Нет доступа"
        )

        return



    await message.answer(
        "👑 Админ панель\n\n"
        "Выберите действие:",
        reply_markup=admin_menu
    )





# =========================
# Меню управления играми
# =========================


@router.callback_query(
    lambda call: call.data == "admin_games"
)
async def games_menu(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    await call.message.edit_text(
        "🎮 Управление играми:",
        reply_markup=games_admin_menu
    )


    await call.answer()





# =========================
# Назад в админку
# =========================


@router.callback_query(
    lambda call: call.data == "back_admin"
)
async def back_admin(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    await call.message.edit_text(
        "👑 Админ панель\n\n"
        "Выберите действие:",
        reply_markup=admin_menu
    )


    await call.answer()

    # =========================
# Добавление игры
# =========================


@router.callback_query(
    lambda call: call.data == "add_game"
)
async def add_game_start(
        call: CallbackQuery,
        state: FSMContext
):

    if not is_admin(call.from_user.id):
        return


    await call.message.answer(
        "🎮 Введите название игры:"
    )


    await state.set_state(
        AddGame.name
    )


    await call.answer()





# =========================
# Получаем название
# =========================


@router.message(
    StateFilter(AddGame.name)
)
async def game_name(
        message: Message,
        state: FSMContext
):

    await state.update_data(
        name=message.text
    )


    await message.answer(
        "💰 Введите цену за 1 день:"
    )


    await state.set_state(
        AddGame.price_1_day
    )





# =========================
# Цена 1 день
# =========================


@router.message(
    StateFilter(AddGame.price_1_day)
)
async def game_price_1_day(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return



    await state.update_data(
        price_1_day=int(message.text)
    )


    await message.answer(
        "💰 Введите цену за 3 дня:"
    )


    await state.set_state(
        AddGame.price_3_days
    )





# =========================
# Цена 3 дня
# =========================


@router.message(
    StateFilter(AddGame.price_3_days)
)
async def game_price_3_days(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return



    await state.update_data(
        price_3_days=int(message.text)
    )


    await message.answer(
        "💰 Введите цену за 7 дней:"
    )


    await state.set_state(
        AddGame.price_7_days
    )





# =========================
# Цена 7 дней
# =========================


@router.message(
    StateFilter(AddGame.price_7_days)
)
async def game_price_7_days(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return



    await state.update_data(
        price_7_days=int(message.text)
    )


    await message.answer(
        "📝 Введите описание игры:"
    )


    await state.set_state(
        AddGame.description
    )





# =========================
# Описание и сохранение
# =========================


@router.message(
    StateFilter(AddGame.description)
)
async def game_description(
        message: Message,
        state: FSMContext
):

    data = await state.get_data()



    add_game(

        data["name"],

        data["price_1_day"],

        data["price_3_days"],

        data["price_7_days"],

        message.text

    )



    await message.answer(

        "✅ Игра добавлена!\n\n"

        f"🎮 {data['name']}\n"

        f"💰 1 день: {data['price_1_day']}₽\n"

        f"💰 3 дня: {data['price_3_days']}₽\n"

        f"💰 7 дней: {data['price_7_days']}₽"

    )



    await state.clear()

# =========================
# Список игр
# =========================

@router.callback_query(
    lambda call: call.data == "list_games"
)
async def list_games(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    games = get_games()


    if not games:

        await call.message.edit_text(
            "📋 Игр пока нет"
        )

        await call.answer()
        return



    text = "📋 Список игр:\n\n"


    for game in games:

        text += (
            f"🎮 {game[1]}\n"
            f"📅 1 день: {game[2]}₽\n"
            f"📅 3 дня: {game[3]}₽\n"
            f"📅 7 дней: {game[4]}₽\n"
            f"📝 {game[5]}\n\n"
        )


    await call.message.edit_text(
        text,
        reply_markup=games_admin_menu
    )


    await call.answer()



# =========================
# Удаление игры - меню
# =========================

@router.callback_query(
    lambda call: call.data == "delete_game"
)
async def delete_game_menu(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    games = get_games()


    if not games:

        await call.message.edit_text(
            "❌ Игр нет"
        )

        await call.answer()
        return



    buttons = []


    for game in games:

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"❌ {game[1]}",
                    callback_data=f"delete_game_{game[0]}"
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data="admin_games"
            )
        ]
    )


    await call.message.edit_text(
        "❌ Выберите игру для удаления:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await call.answer()


    # =========================
# Удаление выбранной игры
# =========================

@router.callback_query(
    lambda call: call.data.startswith("delete_game_")
)
async def delete_selected_game(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    game_id = int(
        call.data.replace(
            "delete_game_",
            ""
        )
    )


    delete_game_db(game_id)


    await call.answer(
        "✅ Игра удалена",
        show_alert=True
    )


    await call.message.edit_text(
        "🎮 Управление играми:",
        reply_markup=games_admin_menu
    )




# =========================
# Изменение цены
# =========================

@router.callback_query(
    lambda call: call.data == "admin_prices"
)
async def admin_prices(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    games = get_games()


    if not games:

        await call.message.edit_text(
            "❌ Игр нет"
        )

        await call.answer()
        return



    buttons = []


    for game in games:

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"💰 {game[1]}",
                    callback_data=f"price_{game[0]}"
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data="admin_games"
            )
        ]
    )


    await call.message.edit_text(
        "💰 Выберите игру:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await call.answer()


# =========================
# Выбор игры для изменения цены
# =========================

@router.callback_query(
    lambda call: call.data.startswith("price_")
)
async def change_price_start(
        call: CallbackQuery,
        state: FSMContext
):

    if not is_admin(call.from_user.id):
        return


    game_id = int(
        call.data.replace(
            "price_",
            ""
        )
    )


    await state.update_data(
        game_id=game_id
    )


    await call.message.answer(
        "💰 Введите новую цену за 1 день:"
    )


    await state.set_state(
        ChangePrice.price_1_day
    )


    await call.answer()



# =========================
# Цена 1 день
# =========================

@router.message(
    StateFilter(ChangePrice.price_1_day)
)
async def change_price_1_day(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return


    await state.update_data(
        price_1_day=int(message.text)
    )


    await message.answer(
        "💰 Введите цену за 3 дня:"
    )


    await state.set_state(
        ChangePrice.price_3_days
    )



# =========================
# Цена 3 дня
# =========================

@router.message(
    StateFilter(ChangePrice.price_3_days)
)
async def change_price_3_days(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return


    await state.update_data(
        price_3_days=int(message.text)
    )


    await message.answer(
        "💰 Введите цену за 7 дней:"
    )


    await state.set_state(
        ChangePrice.price_7_days
    )



# =========================
# Цена 7 дней и сохранение
# =========================

@router.message(
    StateFilter(ChangePrice.price_7_days)
)
async def change_price_7_days(
        message: Message,
        state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Введите только число"
        )

        return


    data = await state.get_data()


    update_game_price(
        data["game_id"],
        data["price_1_day"],
        data["price_3_days"],
        int(message.text)
    )


    await message.answer(
        "✅ Цена игры успешно изменена"
    )


    await state.clear()



# =========================
# Статистика
# =========================

    # =========================
# Статистика
# =========================

@router.callback_query(
    lambda call: call.data == "admin_stats"
)
async def admin_stats(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    stats = get_today_statistics()


    text = (
        "📊 Статистика за сегодня\n\n"

        f"🎮 Арендовано игр: {stats['count']}\n"
        f"📅 Дней аренды: {stats['days']}\n"
        f"💰 Доход: {stats['profit']}₽\n\n"

        f"📈 Прибыль за день: {stats['profit']}₽"
    )


    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅ Назад",
                        callback_data="back_admin"
                    )
                ]
            ]
        )
    )


    await call.answer()



# =========================
# История обращений
# =========================

@router.callback_query(
    lambda call: call.data == "support_history"
)
async def support_history(call: CallbackQuery):

    if call.from_user.id != ADMIN_ID:
        return


    tickets = get_all_tickets()


    if not tickets:

        await call.message.edit_text(
            "📚 История обращений пустая"
        )

        await call.answer()
        return



    text = "📚 История обращений:\n\n"


    for ticket in tickets[:20]:

        text += (
            f"🎫 #{ticket[0]}\n"
            f"👤 ID: {ticket[1]}\n"
            f"📌 Статус: {ticket[5]}\n"
            f"💬 {ticket[3][:50]}\n\n"
        )


    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅ Назад",
                        callback_data="back_admin"
                    )
                ]
            ]
        )
    )


    await call.answer()

    # =========================
# АККАУНТЫ
# =========================


@router.callback_query(
    lambda call: call.data == "admin_accounts"
)
async def admin_accounts(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="➕ Добавить аккаунт",
                    callback_data="add_account"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📋 Список аккаунтов",
                    callback_data="list_accounts"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛠 Тех. работы",
                    callback_data="tech_accounts"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ Удалить аккаунт",
                    callback_data="delete_account"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅ Назад",
                    callback_data="back_admin"
                )
            ]

        ]
    )


    await call.message.edit_text(
        "🎮 Управление аккаунтами:",
        reply_markup=keyboard
    )


    await call.answer()




# =========================
# Добавление аккаунта
# =========================


@router.callback_query(
    lambda call: call.data == "add_account"
)
async def add_account_start(
        call: CallbackQuery,
        state:FSMContext
):


    if not is_admin(call.from_user.id):
        return


    await call.message.answer(
        "🎮 Введите ID игры:"
    )


    await state.set_state(
        AddAccount.game_id
    )


    await call.answer()



@router.message(
    StateFilter(AddAccount.game_id)
)
async def account_game_id(
        message:Message,
        state:FSMContext
):


    await state.update_data(
        game_id=int(message.text)
    )


    await message.answer(
        "👤 Введите логин:"
    )


    await state.set_state(
        AddAccount.login
    )




@router.message(
    StateFilter(AddAccount.login)
)
async def account_login(
        message:Message,
        state:FSMContext
):


    await state.update_data(
        login=message.text
    )


    await message.answer(
        "🔑 Введите пароль:"
    )


    await state.set_state(
        AddAccount.password
    )




@router.message(
    StateFilter(AddAccount.password)
)
async def account_password(
        message:Message,
        state:FSMContext
):


    data = await state.get_data()


    add_account(

        data["game_id"],

        data["login"],

        message.text

    )


    await message.answer(
        "✅ Аккаунт добавлен!"
    )


    await state.clear()




# =========================
# Список аккаунтов
# =========================


@router.callback_query(
    lambda call: call.data == "list_accounts"
)
async def list_accounts(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    accounts = get_all_accounts()


    if not accounts:

        await call.message.edit_text(
            "📋 Аккаунтов нет"
        )

        await call.answer()
        return



    text = "📋 Список аккаунтов:\n\n"

    buttons = []



    for acc in accounts:

        status = {
            "free": "🟢 Свободен",
            "rented": "🔴 Занят",
            "tech": "🛠 Тех. работы"
        }.get(
            acc[3],
            acc[3]
        )


        text += (
            f"🆔 ID: {acc[0]}\n"
            f"🎮 Игра: {acc[1]}\n"
            f"👤 Логин: {acc[2]}\n"
            f"Статус: {status}\n\n"
        )



        if acc[3] == "tech":

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🟢 Вернуть {acc[2]}",
                        callback_data=f"return_acc_{acc[0]}"
                    )
                ]
            )


        else:

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"🛠 Тех. работы {acc[2]}",
                        callback_data=f"tech_{acc[0]}"
                    )
                ]
            )



        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"❌ Удалить {acc[2]}",
                    callback_data=f"delete_acc_{acc[0]}"
                )
            ]
        )



    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data="admin_accounts"
            )
        ]
    )



    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )


    await call.answer()

    # =========================
# Отправить аккаунт на тех. работы
# =========================

@router.callback_query(
    lambda call: call.data.startswith("tech_")
)
async def tech_account(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    account_id = int(
        call.data.replace(
            "tech_",
            ""
        )
    )


    set_account_tech(account_id)


    await call.answer(
        "🛠 Аккаунт отправлен на тех. работы",
        show_alert=True
    )


    await call.message.edit_text(
        "✅ Статус аккаунта изменён",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅ Назад",
                        callback_data="list_accounts"
                    )
                ]
            ]
        )
    )



# =========================
# Удаление аккаунта
# =========================

@router.callback_query(
    lambda call: call.data.startswith("delete_acc_")
)
async def delete_selected_account(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    account_id = int(
        call.data.replace(
            "delete_acc_",
            ""
        )
    )


    delete_account(account_id)


    await call.answer(
        "❌ Аккаунт удалён",
        show_alert=True
    )


    await call.message.edit_text(
        "✅ Аккаунт удалён",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📋 Список аккаунтов",
                        callback_data="list_accounts"
                    )
                ]
            ]
        )
    )

    # =========================
# Вернуть аккаунт в работу
# =========================

@router.callback_query(
    lambda call: call.data.startswith("return_acc_")
)
async def return_account(call: CallbackQuery):

    if not is_admin(call.from_user.id):
        return


    account_id = int(
        call.data.replace(
            "return_acc_",
            ""
        )
    )


    return_account_from_tech(
        account_id
    )


    await call.answer(
        "🟢 Аккаунт снова доступен",
        show_alert=True
    )


    await call.message.edit_text(
        "✅ Аккаунт возвращён в работу",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📋 Список аккаунтов",
                        callback_data="list_accounts"
                    )
                ]
            ]
        )
    )