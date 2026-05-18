import psycopg2



def create_db(conn):
    """Создание таблиц"""

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(id)
                ON DELETE CASCADE,
                phone VARCHAR(20) UNIQUE
            );
        """)

    conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    """Добавление нового клиента"""

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients(first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (first_name, last_name, email))

        client_id = cur.fetchone()[0]

        if phones:
            for phone in phones:
                cur.execute("""
                    INSERT INTO phones(client_id, phone)
                    VALUES (%s, %s);
                """, (client_id, phone))

    conn.commit()
    return client_id


def add_phone(conn, client_id, phone):
    """Добавление телефона существующему клиенту"""

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phones(client_id, phone)
            VALUES (%s, %s);
        """, (client_id, phone))

    conn.commit()


def change_client(conn, client_id,
                  first_name=None,
                  last_name=None,
                  email=None):
    """Изменение данных клиента"""

    with conn.cursor() as cur:

        if first_name:
            cur.execute("""
                UPDATE clients
                SET first_name = %s
                WHERE id = %s;
            """, (first_name, client_id))

        if last_name:
            cur.execute("""
                UPDATE clients
                SET last_name = %s
                WHERE id = %s;
            """, (last_name, client_id))

        if email:
            cur.execute("""
                UPDATE clients
                SET email = %s
                WHERE id = %s;
            """, (email, client_id))

    conn.commit()


def delete_phone(conn, client_id, phone):
    """Удаление телефона клиента"""

    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))

    conn.commit()


def delete_client(conn, client_id):
    """Удаление клиента"""

    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients
            WHERE id = %s;
        """, (client_id,))

    conn.commit()


def find_client(conn,
                first_name=None,
                last_name=None,
                email=None,
                phone=None):
    """Поиск клиента"""

    with conn.cursor() as cur:

        query = """
            SELECT c.id,
                   c.first_name,
                   c.last_name,
                   c.email,
                   p.phone
            FROM clients c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE 1=1
        """

        params = []

        if first_name:
            query += " AND c.first_name = %s"
            params.append(first_name)

        if last_name:
            query += " AND c.last_name = %s"
            params.append(last_name)

        if email:
            query += " AND c.email = %s"
            params.append(email)

        if phone:
            query += " AND p.phone = %s"
            params.append(phone)

        cur.execute(query, params)

        return cur.fetchall()


if __name__ == '__main__':

    conn = psycopg2.connect(
        database="clients_db",
        user="postgres",
        password="your_password",
        host="localhost",
        port="5432"
    )

    create_db(conn)

    # Добавление клиента
    client_id = add_client(
        conn,
        "Иван",
        "Иванов",
        "ivan@mail.ru",
        ["111-111", "222-222"]
    )

    # Добавление телефона
    add_phone(conn, client_id, "333-333")

    # Изменение данных клиента
    change_client(conn, client_id, first_name="Петр")

    # Поиск клиента
    result = find_client(conn, first_name="Петр")

    print("Результат поиска:")
    for row in result:
        print(row)

    # Удаление телефона
    delete_phone(conn, client_id, "111-111")

    # Удаление клиента
    delete_client(conn, client_id)

    conn.close()
