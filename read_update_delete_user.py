from db_utils import create_read_query, read_data, update_data, create_update_query
from db_utils import create_delete_query, delete_data

# Função para ler dados do usuário pelo nome, ou pelo usuario_id, ou pelo email, ou pelo status, ou pelo telefone, todos padrao None
def read_user(connection, nome=None, usuario_id=None, email=None, status=None, telefone=None):
    query = create_read_query("usuarios", ["*"])
    if nome:
        query += f" WHERE nome LIKE '{nome}'"
    elif usuario_id:
        query += f" WHERE usuario_id = '{usuario_id}'"
    elif email:
        query += f" WHERE email = '{email}'"
    elif status:
        query += f" WHERE status_usuario = '{status}'"
    elif telefone:
        query += f" WHERE telefone = '{telefone}'"
    result = read_data(connection, query)
    return result


# Função para ler o endereco com base na tabela usuarioendereco usando usuario_id como chave estrangeira
def read_user_address(connection, usuario_id=None):
    query = create_read_query("endereco", ["*"])
    if usuario_id:
        query += f" WHERE endereco_id IN (SELECT endereco_id FROM usuarioendereco WHERE usuario_id = '{usuario_id}')"
    result = read_data(connection, query)
    return result


# Função para imprimir dados completos do usuário com endereço correspondente usando as funções read_user e read_user_address
def print_user_address(connection, usuario_id=None):
    result = read_user_address(connection, usuario_id)
    for row in result:
        print(f"Logradouro: {row[1]}")
        print(f"Número: {row[2]}")
        print(f"Complemento: {row[3]}")
        print(f"Bairro: {row[4]}")
        print(f"Cidade: {row[5]}")
        print(f"Estado (UF): {row[6]}")
        cep = str(row[7])
        print(f"CEP: {cep[:2]}.{cep[2:5]}-{cep[5:]}")



# Função imprimir dados completos do usuário com endereço correspondente usando a função read_user
def print_user(connection, nome=None, usuario_id=None, email=None, status=None, telefone=None):
    result = read_user(connection, nome, usuario_id, email, status, telefone)
    for row in result:
        print(f"Usuário ID: {row[0]}")
        print(f"Nome: {row[1]}")
        print(f"Email: {row[2]}")
        print(f"Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}")
        print(f"Data de cadastro: {row[4]}")
        print(f"Status: {row[5]}")
        print_user_address(connection, row[0])
        print(*"*" * 50)
        print("\n")

# Função atualizar dados do usuário usando função read_user para encontrar o usuário pelo nome, 
# ou pelo usuario_id, ou pelo email, ou pelo status, ou pelo telefone, todos padrao None
def update_user(connection, usuario_id=None, email=None):
    # Primeiro, verificar se o usuário existe
    result = read_user(connection, usuario_id= usuario_id, email= email)
    if not result:
        print("Usuário não encontrado.")
        return False

    for row in result:
        # Exibir dados atuais do usuário
        print("\n=== Dados Atuais do Usuário ===")
        print(f"Usuário ID: {row[0]}")
        print(f"Nome: {row[1]}")
        print(f"Email: {row[2]}")
        print(f"Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}")
        print(f"Data de cadastro: {row[4]}")
        print(f"Status: {row[5]}")
        print("\n=== Endereço Atual ===")
        print_user_address(connection, row[0])
        print("=" * 50)

        # Confirmar atualização
        if not confirm_action("Deseja atualizar o usuário?"):
            continue

        # Dicionário para armazenar as alterações
        updates = {}

        while True:
            print("\nOpções de atualização:")
            print("1 - Nome")
            print("2 - Email")
            print("3 - Telefone")
            print("4 - Status")
            print("5 - Endereço")
            print("0 - Finalizar alterações")

            opcao = input("Escolha uma opção (0-5): ").strip()

            if opcao == "0":
                break

            if opcao not in ["1", "2", "3", "4", "5"]:
                print("Opção inválida!")
                continue

            if opcao == "1":
                novo_nome = input("Novo nome: ").strip()
                if novo_nome:
                    updates['nome'] = novo_nome

            elif opcao == "2":
                novo_email = input("Novo email: ").strip()
                if novo_email:
                    updates['email'] = novo_email

            elif opcao == "3":
                novo_telefone = input("Novo telefone (apenas números): ").strip()
                if novo_telefone.isdigit() and len(novo_telefone) == 11:
                    updates['telefone'] = novo_telefone
                else:
                    print("Telefone inválido! Use apenas números (11 dígitos)")

            elif opcao == "4":
                novo_status = input("Novo status (Ativo/Inativo): ").strip().capitalize()
                if novo_status in ['Ativo', 'Inativo']:
                    updates['status_usuario'] = novo_status
                else:
                    print("Status inválido! Use 'Ativo' ou 'Inativo'")

            elif opcao == "5":
                atualizar_endereco(connection, row[0])

        # Realizar atualização no banco de dados
        if updates:
            try:
                condition = f"usuario_id = {row[0]}"
                query = create_update_query("usuarios", updates.keys(), condition)
                update_data(connection, query, tuple(updates.values()))
                print("\nUsuário atualizado com sucesso!")

                # Exibir dados atualizados
                print("\n=== Dados Atualizados ===")
                result = read_user(connection, usuario_id=row[0])
                for updated_row in result:
                    print(f"Nome: {updated_row[1]}")
                    print(f"Email: {updated_row[2]}")
                    print(f"Telefone: ({updated_row[3][:2]}) {updated_row[3][2:7]}-{updated_row[3][7:]}")
                    print(f"Status: {updated_row[5]}")

            except Exception as e:
                print(f"Erro ao atualizar usuário: {str(e)}")
                return False

    return True

def atualizar_endereco(connection, usuario_id):
    """Função auxiliar para atualizar endereço"""
    endereco_updates = {}

    print("\nOpções de atualização de endereço:")
    opcoes = {
        "1": ("logradouro", "Logradouro"),
        "2": ("numero", "Número"),
        "3": ("complemento", "Complemento"),
        "4": ("bairro", "Bairro"),
        "5": ("cidade", "Cidade"),
        "6": ("estado", "Estado (UF)"),
        "7": ("cep", "CEP")
    }

    for key, (_, label) in opcoes.items():
        print(f"{key} - {label}")

    opcao = input("Escolha o campo para atualizar (1-7): ").strip()

    if opcao in opcoes:
        campo, label = opcoes[opcao]
        novo_valor = input(f"Novo {label}: ").strip()

        if novo_valor:
            try:
                # Primeiro, obtemos o endereco_id
                query = f"""
                SELECT endereco_id 
                FROM usuarioendereco 
                WHERE usuario_id = {usuario_id}
                """
                result = read_data(connection, query)
                if result and result[0]:
                    endereco_id = result[0][0]
                    condition = f"endereco_id = {endereco_id}"
                    query = create_update_query("endereco", [campo], condition)
                    update_data(connection, query, (novo_valor,))
                    print(f"{label} atualizado com sucesso!")
                else:
                    print("Endereço não encontrado para este usuário.")
            except Exception as e:
                print(f"Erro ao atualizar endereço: {str(e)}")

def confirm_action(message):
    """Função auxiliar para confirmar ações"""
    while True:
        response = input(f"\n{message} (S/N): ").upper().strip()
        if response in ['S', 'N']:
            return response == 'S'
        print("Por favor, responda com S ou N.")


# Função deletar usuário da tabela usuarios usando a função read_user para encontrar o usuário usuario_id ou email e se houver, deletar o usuário e o endereço correspondente
def delete_user(connection, usuario_id=None, email=None):
    # Primeiro, verificar se o usuário existe
    result = read_user(connection, usuario_id= usuario_id, email= email)
    if not result:
        print("Usuário não encontrado.")
        return False

    for row in result:
        # Exibir dados do usuário
        print("\n=== Dados do Usuário ===")
        print(f"Usuário ID: {row[0]}")
        print(f"Nome: {row[1]}")
        print(f"Email: {row[2]}")
        print(f"Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}")
        print(f"Data de cadastro: {row[4]}")
        print(f"Status: {row[5]}")
        print("\n=== Endereço ===")
        print_user_address(connection, row[0])
        print("=" * 50)

        # Confirmar exclusão
        if not confirm_action("Deseja excluir o usuário?"):
            continue

        # Realizar exclusão no banco de dados
        try:
            # Iniciar transação
            connection.start_transaction()

            # endereco_id
            condition_endereco = read_user_address(connection, row[0])[0][0]

            # Deletar o row na tabela usuarioendereco
            condition_usuarioendereco = f"usuario_id = {row[0]}"
            query = create_delete_query("usuarioendereco", condition_usuarioendereco)
            delete_data(connection, query, None)

            # Deletar o row na tabela endereco
            query = create_delete_query("endereco", condition_endereco)
            delete_data(connection, query, None)

            # Deletar o row na tabela usuarios  
            condition = f"usuario_id = {row[0]}"
            query = create_delete_query("usuarios", condition)
            delete_data(connection, query, None)

            # Confirmar transação
            connection.commit()
            print("\nUsuário e dados relacionados excluídos com sucesso!")

        except Exception as e:
            # Em caso de erro, reverter todas as alterações
            connection.rollback()
            print(f"Erro ao excluir usuário: {str(e)}")
            print("Todas as alterações foram revertidas.")
            return False


    return True