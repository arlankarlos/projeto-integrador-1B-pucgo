from db_utils import create_insert_query, insert_data, create_read_query, read_data
from validate_utils import (
    validate_isbn,
    validate_year,
    validate_location,
    check_author_exists,
)


# Função para ler a entrada de dados da categoria, nome e descricao
def read_category_data():
    nome = input("Nome: ")
    descricao = input("Descricao: ")
    return (nome, descricao)


# Função para adicionar uma nova categoria na tabela de categorias, categoria_id, nome, descricao
def add_category(connection):
    query = create_insert_query("categorias", ["nome", "descricao"])
    values = read_category_data()
    insert_data(connection, query, values)


# Função para ler os dados de um autor, nome, nacionalidade
def read_author_data():
    nome = input("Nome: ").strip()
    nacionalidade = input("Nacionalidade: ").strip()
    return (nome, nacionalidade)


# Função para adicionar um novo autor na tabela de autores, nome, nacionalidade
def add_author(connection):
    query = create_insert_query("autores", ["nome", "nacionalidade"])
    values = read_author_data()
    insert_data(connection, query, values)


# Função para ler os dados de um livro, título, isbn, ano_publicacao, editora, quantidade_copias, localizacao_estante
def read_book_data(connection):
    while (
        not (categoria_id := input("Categoria ID: ").strip()).isdigit()
        or len(categoria_id) != 2
    ):
        print("Categoria ID inválida - tente novamente (2 digitos)\n 01")

    contador_autores = int(input("Quantidade de autores: ").strip())
    lista_autores = []
    while contador_autores > 0:
        if not (autor_id := input("Autor ID: ").strip()).isdigit() or len(autor_id) > 4:
            print(
                "Autor ID inválida - tente novamente (digitos exatos sem 0 a esquerda)\n 1"
            )
            continue
        if not check_author_exists(connection, int(autor_id)):
            print("Autor ID inválido - tente novamente (autor não cadastrado)\n 1")
            continue
        lista_autores.append(int(autor_id))
        contador_autores -= 1


    titulo = input("Titulo: ").strip()
    while not titulo:
        print("O título não pode estar vazio. Tente novamente.")
        titulo = input("Titulo: ").strip()

    while not validate_isbn(isbn := input("ISBN: ").strip()):
        print("ISBN inválido - tente novamente (13 digitos)\n 1234567890123")

    while not validate_year(ano_publicacao := input("Ano de publicacao: ").strip()):
        print("Ano inválido - tente novamente (4 digitos)\n 2023")

    editora = input("Editora: ").strip()
    while not editora:
        print("A editora não pode estar vazia. Tente novamente.")
        editora = input("Editora: ").strip()

    while (
        not (quantidade_copias := input("Quantidade de copias: ").strip()).isdigit()
        or len(quantidade_copias) != 2
    ):
        print("Quantidade de copias inválida - tente novamente (2 digitos)\n 10")

    while not validate_location(
        localizacao_estante := input("Localizacao da estante: ").strip()
    ):
        print("Localizacao da estante inválida - tente novamente (5 digitos)\n ABC45")
    return (
        categoria_id,
        lista_autores,
        titulo,
        isbn,
        ano_publicacao,
        editora,
        quantidade_copias,
        localizacao_estante,
    )


# Função para adicionar um novo livro na tabela de livros, categoria_id, titulo, isbn, ano_publicacao, editora, quantidade_copias, localizacao_estante
def add_book(connection):
    # Adiciona livro no banco de dados
    query = create_insert_query(
        "livros",
        [
            "titulo",
            "isbn",
            "ano_publicacao",
            "editora",
            "quantidade_copias",
            "localizacao_estante",
        ],
    )
    values = read_book_data(connection)
    insert_data(connection, query, values[2:])

    # Obtem o livro_id do livro adicionado
    query = create_read_query("livros", ["livro_id"])
    result = read_data(connection, query)
    result.sort() # type: ignore
    livro_id = result[-1][0] # type: ignore

    # Preenche a tabela livroscategorias com o livro_id e a categoria_id
    query = create_insert_query("livroscategorias", ["livro_id", "categoria_id"])
    values_livroscategorias = (livro_id, values[0])
    insert_data(connection, query, values_livroscategorias)

    # Preenche a tabela livrosautores com o livro_id e o autor_id
    for autor_id in values[1]:
        query = create_insert_query("livrosautores", ["livro_id", "autor_id"])
        values_livrosautores = (livro_id, autor_id)
        insert_data(connection, query, values_livrosautores)
