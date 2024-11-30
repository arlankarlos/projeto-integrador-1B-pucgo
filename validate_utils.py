from db_utils import create_read_query, read_data


# Função completa validar email
def validate_email(email):
    return "@" in email and "." in email and email.index("@") < email.index(".")

# Função validar telefone
def validate_phone(phone):
    return phone.isdigit() and len(phone) == 11

# Função validar CEP
def validate_cep(cep):
    return cep.isdigit() and len(cep) == 8

# Função validar Estado UF com 2 letras
def validate_uf(uf):
    return uf.isalpha() and len(uf) == 2

# Função validar ISBN
def validate_isbn(isbn):
    return isbn.isdigit() and len(isbn) == 13

# Função validar ano
def validate_year(year):
    return year.isdigit() and len(year) == 4

# Função validar localização da estante
def validate_location(location):
    if len(location) != 5:
        return False
    if not location[:3].isalpha():
        return False
    if not location[3:].isdigit():
        return False
    return True


# Função validar existência de um autor na base de dados 
def check_author_exists(connection, autor_id):
    query = create_read_query("autores", ["autor_id"])
    result = read_data(connection, query)
    return any(row[0] == autor_id for row in result)