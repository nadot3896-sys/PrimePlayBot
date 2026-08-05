from database.db import connect
from datetime import datetime, timedelta



# =========================
# Добавление аренды (дни)
# =========================

def add_rental(
        telegram_id,
        game_id,
        days,
        price,
        account_id=None
):

    connection = connect()
    cursor = connection.cursor()


    start = datetime.now()

    end = start + timedelta(days=days)


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
            days * 24,
            float(price),
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S")
        )
    )


    connection.commit()
    connection.close()





# =========================
# Получить аренду
# =========================

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


    rental = cursor.fetchone()

    connection.close()


    return rental





# =========================
# Проверка аренды
# =========================

def has_rental(
        telegram_id,
        game_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id
        FROM rentals
        WHERE telegram_id=?
        AND game_id=?
        """,
        (
            telegram_id,
            game_id
        )
    )


    result = cursor.fetchone()


    connection.close()


    return result is not None





# =========================
# Активные аренды
# =========================

def get_user_rentals(
        telegram_id
):

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


    rentals = cursor.fetchall()


    connection.close()


    return rentals





# =========================
# Продление аренды
# =========================

def extend_rental(
        rental_id,
        days,
        price
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


    new_end = old_end + timedelta(
        days=days
    )



    cursor.execute(
        """
        UPDATE rentals

        SET

        hours = hours + ?,

        price = price + ?,

        end_time = ?

        WHERE id=?

        """,
        (
            days * 24,
            price,
            new_end.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            rental_id
        )
    )


    connection.commit()
    connection.close()


    return True





# =========================
# Отмена аренды
# =========================

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
        start_time,
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

    total_price = float(rental[1])


    start = datetime.strptime(
        rental[2],
        "%Y-%m-%d %H:%M:%S"
    )


    end = datetime.strptime(
        rental[3],
        "%Y-%m-%d %H:%M:%S"
    )


    now = datetime.now()


    total_time = (
        end - start
    ).total_seconds()


    used_time = (
        now - start
    ).total_seconds()



    # защита от выхода за границы
    used_time = max(
        0,
        min(
            used_time,
            total_time
        )
    )


    # сколько реально человек использовал
    spent = round(
        total_price *
        (
            used_time / total_time
        ),
        2
    ) if total_time > 0 else 0



    # сколько вернуть
    refund = round(
        total_price - spent,
        2
    )



    # Начисляем только реально использованное время
    cursor.execute(
        """
        UPDATE users

        SET total_spent = total_spent + ?

        WHERE telegram_id=?

        """,
        (
            spent,
            telegram_id
        )
    )



    # Возврат денег за неиспользованное время
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



    # удаляем аренду
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
# Количество аренд
# =========================

def get_rentals_count(
        telegram_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)

        FROM rentals

        WHERE telegram_id=?

        """,
        (
            telegram_id,
        )
    )


    count = cursor.fetchone()[0]


    connection.close()


    return count





# =========================
# Статистика
# =========================

def get_today_statistics():

    connection = connect()
    cursor = connection.cursor()


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    cursor.execute(
        """
        SELECT

        COUNT(*),
        SUM(hours),
        SUM(price)

        FROM rentals

        WHERE start_time LIKE ?

        """,
        (
            today+"%",
        )
    )


    result = cursor.fetchone()


    connection.close()



    if not result[0]:

        return {
            "count":0,
            "days":0,
            "profit":0
        }



    return {

        "count": result[0],

        "days":
            round(result[1]/24,1)
            if result[1]
            else 0,

        "profit":
            result[2]
            if result[2]
            else 0
    }





# =========================
# Проверка отзыва
# =========================

def can_leave_review(
        rental_id
):

    connection = connect()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT start_time

        FROM rentals

        WHERE id=?

        """,
        (
            rental_id,
        )
    )


    rental = cursor.fetchone()


    connection.close()



    if not rental:

        return False



    start = datetime.strptime(
        rental[0],
        "%Y-%m-%d %H:%M:%S"
    )



    minutes = (
        datetime.now()-start
    ).total_seconds()/60



    return minutes >= 5