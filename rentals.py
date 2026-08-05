import sqlite3
from datetime import datetime, timedelta


DATABASE = "users.db"


# =====================================================
# CONNECTION
# =====================================================

def connect():
    return sqlite3.connect(DATABASE)



# =====================================================
# DATABASE INIT
# =====================================================

def create_table():

    connection = connect()
    cursor = connection.cursor()


    # =========================
    # USERS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER UNIQUE,

        full_name TEXT,

        username TEXT,

        balance REAL DEFAULT 0,

        rentals INTEGER DEFAULT 0,

        blocked INTEGER DEFAULT 0,

        referrer_id INTEGER DEFAULT 0,

        referrals INTEGER DEFAULT 0,

        level TEXT DEFAULT 'Новичок',

        total_spent REAL DEFAULT 0

    )
    """)



    # =========================
    # GAMES
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        price_1_day INTEGER DEFAULT 0,

        price_3_days INTEGER DEFAULT 0,

        price_7_days INTEGER DEFAULT 0,

        description TEXT

    )
    """)



    # =========================
    # ACCOUNTS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        game_id INTEGER,

        login TEXT,

        password TEXT,

        status TEXT DEFAULT 'free',

        rating REAL DEFAULT 5,

        complaints INTEGER DEFAULT 0,

        rent_count INTEGER DEFAULT 0,

        reviews_count INTEGER DEFAULT 0

    )
    """)



    # =========================
    # RENTALS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER,

        game_id INTEGER,

        account_id INTEGER,

        hours INTEGER,

        price REAL,

        start_time TEXT,

        end_time TEXT,

        auto_renew INTEGER DEFAULT 0,

        reminder_sent INTEGER DEFAULT 0,

        review_left INTEGER DEFAULT 0

    )
    """)



    # =========================
    # REFERRALS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER UNIQUE,

        referrer_id INTEGER

    )
    """)



    # =========================
    # TICKETS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        username TEXT,

        message TEXT,

        answer TEXT DEFAULT '',

        status TEXT DEFAULT 'Открыт',

        created_at TEXT

    )
    """)



    # =========================
    # HISTORY
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        action TEXT,

        description TEXT,

        created_at TEXT

    )
    """)



    # =========================
    # COMPLAINTS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        account_id INTEGER,

        reason TEXT,

        status TEXT DEFAULT 'Открыта',

        created_at TEXT

    )
    """)



    # =========================
    # TRANSACTIONS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        amount REAL,

        type TEXT,

        description TEXT,

        created_at TEXT

    )
    """)



    # =========================
    # RENTAL HISTORY
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rental_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER,

        game_id INTEGER,

        account_id INTEGER,

        price REAL,

        start_time TEXT,

        end_time TEXT,

        review_left INTEGER DEFAULT 0

    )
    """)



    # =========================
    # REVIEWS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS account_reviews(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        account_id INTEGER,

        user_id INTEGER,

        rating INTEGER,

        review TEXT,

        created_at TEXT

    )
    """)


    connection.commit()
    connection.close()



# =====================================================
# DATABASE FIXES
# =====================================================

def update_database():

    connection = connect()
    cursor = connection.cursor()


    fixes = [

        """
        ALTER TABLE accounts
        ADD COLUMN rent_count INTEGER DEFAULT 0
        """,

        """
        ALTER TABLE accounts
        ADD COLUMN reviews_count INTEGER DEFAULT 0
        """,

        """
        ALTER TABLE rentals
        ADD COLUMN review_left INTEGER DEFAULT 0
        """

    ]


    for fix in fixes:

        try:
            cursor.execute(fix)

        except:
            pass



    connection.commit()
    connection.close()

    # =====================================================
# USERS
# =====================================================


def add_user(
        telegram_id,
        full_name,
        username
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (
            telegram_id,
            full_name,
            username
        )

        VALUES (?, ?, ?)
        """,
        (
            telegram_id,
            full_name,
            username
        )
    )


    connection.commit()
    connection.close()



def user_exists(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE telegram_id=?
        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result



def get_all_users():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        """
    )


    result = cursor.fetchall()


    connection.close()


    return result



# =====================================================
# BALANCE
# =====================================================


def get_balance(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT balance
        FROM users
        WHERE telegram_id=?
        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if result:
        return float(result[0])


    return 0



def update_balance(
        telegram_id,
        amount
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE users

        SET balance=?

        WHERE telegram_id=?
        """,
        (
            amount,
            telegram_id
        )
    )


    connection.commit()
    connection.close()



def change_balance(
        telegram_id,
        amount
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE users

        SET balance = balance + ?

        WHERE telegram_id=?
        """,
        (
            amount,
            telegram_id
        )
    )


    connection.commit()
    connection.close()



# =====================================================
# GAMES
# =====================================================


def add_game(
        name,
        price_1_day,
        price_3_days,
        price_7_days,
        description
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO games
        (
            name,
            price_1_day,
            price_3_days,
            price_7_days,
            description
        )

        VALUES(?,?,?,?,?)
        """,
        (
            name,
            price_1_day,
            price_3_days,
            price_7_days,
            description
        )
    )


    connection.commit()
    connection.close()



def get_games():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM games
        ORDER BY id
        """
    )


    games = cursor.fetchall()


    connection.close()


    return games



def get_game(
        game_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM games
        WHERE id=?
        """,
        (
            game_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result



# =====================================================
# ACCOUNT SYSTEM
# =====================================================


def add_account(
        game_id,
        login,
        password
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO accounts
        (
            game_id,
            login,
            password
        )

        VALUES(?,?,?)
        """,
        (
            game_id,
            login,
            password
        )
    )


    connection.commit()
    connection.close()



def get_free_account(
        game_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            id,
            login,
            password

        FROM accounts

        WHERE game_id=?

        AND status='free'

        ORDER BY rating DESC, rent_count ASC

        LIMIT 1
        """,
        (
            game_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result



def take_account(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE accounts

        SET
        status='rented',
        rent_count = rent_count + 1

        WHERE id=?
        """,
        (
            account_id,
        )
    )


    connection.commit()
    connection.close()



def return_account(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE accounts

        SET status='free'

        WHERE id=?
        """,
        (
            account_id,
        )
    )


    connection.commit()
    connection.close()

    # =====================================================
# RENTALS
# =====================================================

def add_rental(
        telegram_id,
        game_id,
        hours,
        price,
        account_id=None
):

    connection = connect()
    cursor = connection.cursor()

    start = datetime.now()
    end = start + timedelta(hours=hours)

    cursor.execute(
        """
        INSERT INTO rentals
        (
            telegram_id,
            game_id,
            account_id,
            hours,
            price,
            start_time,
            end_time,
            auto_renew,
            reminder_sent,
            review_left
        )

        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            telegram_id,
            game_id,
            account_id,
            hours,
            price,
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
            0,
            0,
            0
        )
    )


    connection.commit()
    connection.close()



def get_user_rentals(telegram_id):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        rentals.id,
        games.name,
        rentals.hours,
        rentals.price,
        rentals.end_time,
        rentals.account_id

        FROM rentals

        JOIN games

        ON rentals.game_id = games.id

        WHERE rentals.telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchall()

    connection.close()

    return result



def get_rental(rental_id):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    result = cursor.fetchone()

    connection.close()

    return result



def extend_rental(
        rental_id,
        hours
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT end_time

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    result = cursor.fetchone()


    if not result:
        connection.close()
        return False



    old_end = datetime.strptime(
        result[0],
        "%Y-%m-%d %H:%M:%S"
    )


    new_end = old_end + timedelta(hours=hours)



    cursor.execute(
        """
        UPDATE rentals

        SET

        hours = hours + ?,

        end_time = ?

        WHERE id=?

        """,
        (
            hours,
            new_end.strftime("%Y-%m-%d %H:%M:%S"),
            rental_id
        )
    )


    connection.commit()
    connection.close()


    return True



# =====================================================
# CANCEL RENTAL
# =====================================================


def cancel_rental(rental_id):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        telegram_id,
        price,
        end_time,
        account_id

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    rental = cursor.fetchone()


    if not rental:

        connection.close()

        return 0



    telegram_id = rental[0]

    price = float(rental[1])

    end_time = datetime.strptime(
        rental[2],
        "%Y-%m-%d %H:%M:%S"
    )


    now = datetime.now()


    seconds = (
        end_time-now
    ).total_seconds()



    if seconds > 0:

        refund = round(
            price * (seconds / 3600),
            2
        )

    else:

        refund = 0



    if refund > 0:

        cursor.execute(
            """
            UPDATE users

            SET balance = balance + ?

            WHERE telegram_id=?

            """,
            (
                refund,
                telegram_id
            )
        )



    cursor.execute(
        """
        DELETE FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    cursor.execute(
        """
        UPDATE accounts

        SET status='free'

        WHERE id=?

        """,
        (
            rental[3],
        )
    )


    connection.commit()
    connection.close()


    return refund

# =========================
# RENTALS
# =========================


def add_rental(
        telegram_id,
        game_id,
        hours,
        price,
        account_id=None
):

    connection = connect()
    cursor = connection.cursor()

    start = datetime.now()
    end = start + timedelta(hours=hours)


    cursor.execute(
        """
        INSERT INTO rentals
        (
            telegram_id,
            game_id,
            account_id,
            hours,
            price,
            start_time,
            end_time
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            game_id,
            account_id,
            hours,
            price,
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S")
        )
    )


    connection.commit()
    connection.close()



def get_user_rentals(telegram_id):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        rentals.id,
        games.name,
        rentals.hours,
        rentals.price,
        rentals.end_time

        FROM rentals

        JOIN games
        ON rentals.game_id = games.id

        WHERE rentals.telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchall()

    connection.close()


    return result



def get_rental(rental_id):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    result = cursor.fetchone()

    connection.close()

    return result



def extend_rental(
        rental_id,
        hours
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT end_time

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    rental = cursor.fetchone()


    if not rental:

        connection.close()
        return False



    old_time = datetime.strptime(
        rental[0],
        "%Y-%m-%d %H:%M:%S"
    )


    new_time = old_time + timedelta(hours=hours)



    cursor.execute(
        """
        UPDATE rentals

        SET

        hours = hours + ?,

        end_time = ?

        WHERE id=?

        """,
        (
            hours,
            new_time.strftime("%Y-%m-%d %H:%M:%S"),
            rental_id
        )
    )


    connection.commit()
    connection.close()


    return True



def cancel_rental(
        rental_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        telegram_id,
        price,
        end_time

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    rental = cursor.fetchone()


    if not rental:

        connection.close()
        return None



    telegram_id = rental[0]
    price = float(rental[1])


    end_time = datetime.strptime(
        rental[2],
        "%Y-%m-%d %H:%M:%S"
    )


    now = datetime.now()


    seconds = (
        end_time - now
    ).total_seconds()



    if seconds > 0:

        refund = round(
            price * (seconds / 3600),
            2
        )

    else:

        refund = 0



    if refund > 0:

        cursor.execute(
            """
            UPDATE users

            SET balance = balance + ?

            WHERE telegram_id=?

            """,
            (
                refund,
                telegram_id
            )
        )


    cursor.execute(
        """
        DELETE FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )



    connection.commit()
    connection.close()


    return refund



# =========================
# USER LEVEL SYSTEM
# =========================


def add_total_spent(
        telegram_id,
        amount
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE users

        SET total_spent = total_spent + ?

        WHERE telegram_id=?

        """,
        (
            amount,
            telegram_id
        )
    )


    connection.commit()
    connection.close()


    update_level_by_spent(
        telegram_id
    )



def update_level_by_spent(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT total_spent

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    if not result:

        connection.close()
        return



    spent = float(result[0])



    if spent >= 15000:

        level = "Premium"

    elif spent >= 5000:

        level = "VIP"

    elif spent >= 1000:

        level = "Игрок"

    else:

        level = "Новичок"



    cursor.execute(
        """
        UPDATE users

        SET level=?

        WHERE telegram_id=?

        """,
        (
            level,
            telegram_id
        )
    )


    connection.commit()
    connection.close()

    # =========================
# REFERRALS
# =========================


def add_referral(
        user_id,
        referrer_id
):

    if user_id == referrer_id:
        return False


    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id

        FROM referrals

        WHERE user_id=?

        """,
        (
            user_id,
        )
    )


    if cursor.fetchone():

        connection.close()
        return False



    cursor.execute(
        """
        INSERT INTO referrals
        (
            user_id,
            referrer_id
        )

        VALUES (?,?)

        """,
        (
            user_id,
            referrer_id
        )
    )


    cursor.execute(
        """
        UPDATE users

        SET referrals = referrals + 1,
        balance = balance + 20

        WHERE telegram_id=?

        """,
        (
            referrer_id,
        )
    )


    cursor.execute(
        """
        UPDATE users

        SET referrer_id=?

        WHERE telegram_id=?

        """,
        (
            referrer_id,
            user_id
        )
    )


    connection.commit()
    connection.close()


    return True



def get_referrals_count(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)

        FROM referrals

        WHERE referrer_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()[0]


    connection.close()


    return result



# =========================
# SUPPORT SYSTEM
# =========================


def create_ticket(
        user_id,
        username,
        message
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO tickets
        (
            user_id,
            username,
            message,
            created_at
        )

        VALUES (?,?,?,?)

        """,
        (
            user_id,
            username,
            message,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    connection.commit()
    connection.close()



def get_open_tickets():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM tickets

        WHERE status='Открыт'

        ORDER BY id DESC

        """
    )


    result = cursor.fetchall()


    connection.close()


    return result



def get_ticket(
        ticket_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM tickets

        WHERE id=?

        """,
        (
            ticket_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result



def close_ticket(
        ticket_id,
        answer
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE tickets

        SET

        answer=?,

        status='Закрыт'

        WHERE id=?

        """,
        (
            answer,
            ticket_id
        )
    )


    connection.commit()
    connection.close()



# =========================
# TRANSACTIONS
# =========================


def add_transaction(
        user_id,
        amount,
        transaction_type,
        description
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            amount,
            type,
            description,
            created_at
        )

        VALUES (?,?,?,?,?)

        """,
        (
            user_id,
            amount,
            transaction_type,
            description,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    connection.commit()
    connection.close()

    # =====================================================
# ACCOUNT MANAGEMENT
# =====================================================


def get_all_accounts():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        accounts.id,
        games.name,
        accounts.login,
        accounts.status,
        accounts.rating,
        accounts.rent_count

        FROM accounts

        JOIN games

        ON accounts.game_id = games.id

        ORDER BY accounts.id DESC

        """
    )


    result = cursor.fetchall()


    connection.close()


    return result



def set_account_status(
        account_id,
        status
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE accounts

        SET status=?

        WHERE id=?

        """,
        (
            status,
            account_id
        )
    )


    connection.commit()
    connection.close()



def delete_account(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM accounts

        WHERE id=?

        """,
        (
            account_id
        )
    )


    connection.commit()
    connection.close()



# =====================================================
# REVIEWS
# =====================================================


def add_account_review(
        account_id,
        user_id,
        rating,
        review
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO account_reviews
        (
            account_id,
            user_id,
            rating,
            review,
            created_at
        )

        VALUES (?,?,?,?,?)

        """,
        (
            account_id,
            user_id,
            rating,
            review,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    connection.commit()


    update_account_rating(
        account_id
    )


    connection.close()



def update_account_rating(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT

        AVG(rating),
        COUNT(*)

        FROM account_reviews

        WHERE account_id=?

        """,
        (
            account_id,
        )
    )


    result = cursor.fetchone()


    rating = 5


    if result[0]:

        rating = round(
            result[0],
            2
        )


    cursor.execute(
        """
        UPDATE accounts

        SET

        rating=?,

        reviews_count=?

        WHERE id=?

        """,
        (
            rating,
            result[1],
            account_id
        )
    )


    connection.commit()
    connection.close()



# =====================================================
# HISTORY
# =====================================================


def add_history(
        user_id,
        action,
        description
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO history
        (
            user_id,
            action,
            description,
            created_at
        )

        VALUES (?,?,?,?)

        """,
        (
            user_id,
            action,
            description,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    connection.commit()
    connection.close()



def get_user_history(
        user_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM history

        WHERE user_id=?

        ORDER BY id DESC

        """,
        (
            user_id,
        )
    )


    result = cursor.fetchall()


    connection.close()


    return result



# =====================================================
# COMPLAINTS
# =====================================================


def add_complaint(
        user_id,
        account_id,
        reason
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO complaints
        (
            user_id,
            account_id,
            reason,
            created_at
        )

        VALUES (?,?,?,?)

        """,
        (
            user_id,
            account_id,
            reason,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    connection.commit()
    connection.close()



def get_complaints():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM complaints

        ORDER BY id DESC

        """
    )


    result = cursor.fetchall()


    connection.close()


    return result



# =====================================================
# USER LEVEL
# =====================================================


def get_user_level(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT level

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if result:

        return result[0]


    return "Новичок"



def get_total_spent(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT total_spent

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if result:

        return result[0]


    return 0



# =====================================================
# USER BLOCK
# =====================================================


def block_user(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE users

        SET blocked=1

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    connection.commit()
    connection.close()



def unblock_user(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE users

        SET blocked=0

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    connection.commit()
    connection.close()



def is_blocked(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT blocked

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if result:

        return result[0] == 1


    return False

# =====================================================
# COMPATIBILITY FUNCTIONS
# =====================================================

def update_users_table():

    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN level TEXT DEFAULT 'Новичок'
        """)
    except:
        pass


    try:
        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN total_spent REAL DEFAULT 0
        """)
    except:
        pass


    connection.commit()
    connection.close()



def update_games_table():

    connection = connect()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        ALTER TABLE games
        ADD COLUMN price_1_day INTEGER DEFAULT 0
        """)
    except:
        pass


    try:
        cursor.execute("""
        ALTER TABLE games
        ADD COLUMN price_3_days INTEGER DEFAULT 0
        """)
    except:
        pass


    try:
        cursor.execute("""
        ALTER TABLE games
        ADD COLUMN price_7_days INTEGER DEFAULT 0
        """)
    except:
        pass


    connection.commit()
    connection.close()

    # =====================================================
# UPDATE RENTALS TABLE
# =====================================================

def update_rentals_table():

    connection = connect()
    cursor = connection.cursor()


    try:
        cursor.execute(
            """
            ALTER TABLE rentals
            ADD COLUMN auto_renew INTEGER DEFAULT 0
            """
        )

    except:
        pass


    try:
        cursor.execute(
            """
            ALTER TABLE rentals
            ADD COLUMN reminder_sent INTEGER DEFAULT 0
            """
        )

    except:
        pass


    try:
        cursor.execute(
            """
            ALTER TABLE rentals
            ADD COLUMN review_left INTEGER DEFAULT 0
            """
        )

    except:
        pass


    connection.commit()
    connection.close()

    # =====================================================
# REFERRER CHECK
# =====================================================

def has_referrer(
        user_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id

        FROM referrals

        WHERE user_id=?

        """,
        (
            user_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result is not None

# =====================================================
# LEVEL PROGRESS
# =====================================================

def get_level_progress(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            total_spent,
            level

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if not result:

        return {
            "spent": 0,
            "level": "Новичок",
            "next": 1000,
            "left": 1000,
            "percent": 0
        }


    spent = float(result[0] or 0)
    level = result[1] or "Новичок"


    if spent < 1000:

        next_level = 1000

    elif spent < 5000:

        next_level = 5000

    elif spent < 15000:

        next_level = 15000

    else:

        next_level = 15000



    left = max(
        next_level - spent,
        0
    )


    if next_level == 0:

        percent = 100

    else:

        percent = min(
            int((spent / next_level) * 100),
            100
        )


    return {
        "spent": spent,
        "level": level,
        "next": next_level,
        "left": left,
        "percent": percent
    }

# =====================================================
# USER DISCOUNT SYSTEM
# =====================================================

def get_user_discount(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT level

        FROM users

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    result = cursor.fetchone()


    connection.close()


    if not result:
        return 0


    level = result[0]


    discounts = {

        "Новичок": 0,

        "Игрок": 3,

        "VIP": 7,

        "Premium": 15

    }


    return discounts.get(
        level,
        0
    )

# =====================================================
# GET ALL TICKETS
# =====================================================

def get_all_tickets():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *

        FROM tickets

        ORDER BY id DESC

        """
    )


    tickets = cursor.fetchall()


    connection.close()


    return tickets

# =====================================================
# SET ACCOUNT TECH MODE
# =====================================================

def set_account_tech(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE accounts

        SET status='tech'

        WHERE id=?

        """,
        (
            account_id,
        )
    )


    connection.commit()
    connection.close()

    # =====================================================
# RETURN ACCOUNT FROM TECH MODE
# =====================================================

def return_account_from_tech(
        account_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE accounts

        SET status='free'

        WHERE id=?

        """,
        (
            account_id,
        )
    )


    connection.commit()
    connection.close()

    # =====================================================
# FIX ACCOUNTS TABLE
# =====================================================

def fix_accounts_table():

    connection = connect()
    cursor = connection.cursor()


    columns = [
        "rating REAL DEFAULT 5",
        "complaints INTEGER DEFAULT 0",
        "rent_count INTEGER DEFAULT 0",
        "reviews_count INTEGER DEFAULT 0"
    ]


    for column in columns:

        try:
            cursor.execute(
                f"""
                ALTER TABLE accounts
                ADD COLUMN {column}
                """
            )

        except:
            pass


    connection.commit()
    connection.close()