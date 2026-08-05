from database.db import connect





# =========================
# Добавить игру
# =========================


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

        VALUES (?, ?, ?, ?, ?)

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






# =========================
# Получить все игры
# =========================


def get_games():

    connection = connect()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
        id,
        name,
        price_1_day,
        price_3_days,
        price_7_days,
        description

        FROM games

        ORDER BY id DESC
        """
    )


    games = cursor.fetchall()


    connection.close()


    return games






# =========================
# Получить одну игру
# =========================


def get_game(game_id):

    connection = connect()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
        id,
        name,
        price_1_day,
        price_3_days,
        price_7_days,
        description

        FROM games

        WHERE id=?

        """,

        (
            game_id,
        )
    )


    game = cursor.fetchone()


    connection.close()


    return game






# =========================
# Удалить игру
# =========================


def delete_game(game_id):

    connection = connect()

    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM games

        WHERE id=?

        """,

        (
            game_id,
        )
    )


    connection.commit()

    connection.close()






# =========================
# Изменить цену
# =========================


def update_game_price(
        game_id,
        price_1_day,
        price_3_days,
        price_7_days
):

    connection = connect()

    cursor = connection.cursor()



    cursor.execute(
        """
        UPDATE games

        SET

        price_1_day=?,

        price_3_days=?,

        price_7_days=?


        WHERE id=?

        """,

        (
            price_1_day,
            price_3_days,
            price_7_days,
            game_id
        )
    )



    connection.commit()

    connection.close()