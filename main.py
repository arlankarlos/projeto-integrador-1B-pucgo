from db_utils import get_database_connection
from interface import create_interface


def main():
    connection = get_database_connection()
    if connection:
        try:
            app = create_interface(connection)
            app.run()

        finally:
            if connection.is_connected():
                connection.close()
                print("Conexão ao banco de dados MySQL encerrada")


if __name__ == "__main__":
    main()
