from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message
)

from database.db import (
    get_all_accounts,
    add_account,
    delete_account,
    set_account_status
)


router = Router()


ADMIN_ID = 7576530147