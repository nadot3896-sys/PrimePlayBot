from database.db import connect



# Получить всех пользователей

def get_users():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT telegram_id, username
        FROM users
        """
    )


    users = cursor.fetchall()


    connection.close()

    return users



# Количество пользователей

def get_users_count():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    )


    count = cursor.fetchone()[0]


    connection.close()

    return count



# Количество игр

def get_games_count():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM games
        """
    )


    count = cursor.fetchone()[0]


    connection.close()

    return count



# Количество аренд

def get_rentals_count():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM rentals
        """
    )


    count = cursor.fetchone()[0]


    connection.close()

    return count



# Общий баланс пользователей

def get_total_balance():

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT SUM(balance)
        FROM users
        """
    )


    total = cursor.fetchone()[0]


    connection.close()


    return total or 0