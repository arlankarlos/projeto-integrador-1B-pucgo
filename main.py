from db_utils import get_database_connection
from create_user import create_user, read_user_address_id, create_user_address
from add_to_invetory import add_book, add_author, add_category
from validate_utils import check_author_exists
from read_update_delete_user import print_user, update_user, delete_user


def main():
    connection = get_database_connection()
    if connection:
        try:
            # add_author(connection)
            # add_category(connection)
            # add_book(connection)
            # print(check_author_exists(connection, 1))
            # create_user(connection)
            # create_user_address(connection)
            # print_user(connection, nome="Karlos")
            # update_user(connection, email="updated@gmail.com")
            # delete_user(connection, email="updated@gmail.com")
            delete_user(connection, usuario_id=6)

        finally:
            if connection.is_connected():
                connection.close()
                print("Conexão ao banco de dados MySQL encerrada")


if __name__ == "__main__":
    main()
