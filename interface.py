import tkinter as tk
from tkinter import messagebox, ttk
from db_utils import get_database_connection, create_update_query, update_data
from read_update_delete_user import (
    create_delete_query,
    delete_data,
    read_user,
    read_user_address,
    read_data,
)
from create_user import create_insert_query, insert_data, get_usuario_id_endereco_id
from validate_utils import validate_email, validate_phone, validate_cep, validate_uf
import datetime
from interface_author import AuthorManagementInterface
from interface_categories import CategoriesManagementInterface
from interface_books import BooksManagementInterface
from interface_borrow import BorrowManagementInterface


class UserManagementInterface:
    def __init__(self, connection=None):
        self.connection = connection
        self.root = tk.Tk()
        self.root.title("Gerenciamento de Usuários")
        self.root.geometry("800x600")

        # Configurando estilo
        self.configure_style()

        # Criando frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")

        # Criando os botões inicialmente
        self.create_buttons()

        # Exibir a interface inicial
        self.home_interface()

    def ensure_connection(self):
        """
        Verifica se a conexão está ativa e tenta reconectar se necessário
        """
        if not self.connection or not self.connection.is_connected():
            self.connection = get_database_connection()
            if not self.connection:
                messagebox.showerror(
                    "Erro", "Não foi possível conectar ao banco de dados!"
                )
                return False
        return True

    def configure_style(self):
        self.root.configure(bg="#f0f0f0")
        self.button_style = {
            "font": ("Arial", 11),
            "width": 20,
            "bg": "#4CAF50",
            "fg": "white",
            "relief": tk.RAISED,
            "cursor": "hand2",
        }

    def home_interface(self):
        """Interface inicial do sistema"""
        self.clear_right_frames()

        # Criar frame principal para a home
        home_frame = tk.Frame(
            self.main_frame,
            bg="#2c3e50"  # Cor de fundo escura para contraste
        )
        home_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Configurar o grid para centralizar o conteúdo
        home_frame.grid_columnconfigure(0, weight=1)
        home_frame.grid_rowconfigure(0, weight=1)

        # Criar label com o título
        title_label = tk.Label(
            home_frame,
            text="Gestão de Biblioteca",
            font=("Helvetica", 36, "bold"),
            fg="white",
            bg="#2c3e50",
            pady=20
        )
        title_label.grid(row=0, column=0, sticky="n", pady=50)

        # Adicionar subtítulo ou descrição (opcional)
        subtitle_label = tk.Label(
            home_frame,
            text="Sistema de Gerenciamento Bibliotecário",
            font=("Helvetica", 16),
            fg="white",
            bg="#2c3e50"
        )
        subtitle_label.grid(row=1, column=0, sticky="n")

        # Configurar o frame principal para expandir
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def create_user_fields(self):
        """Cria os campos de dados do usuário"""
        self.user_frame = tk.LabelFrame(
            self.main_frame, text="Dados do Usuário", padx=10, pady=5
        )
        self.user_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=5
        )  # Colocando à direita

        # Campo Nome
        tk.Label(self.user_frame, text="Nome:").grid(
            row=1, column=0, sticky="e", pady=2
        )
        self.name_entry = tk.Entry(self.user_frame)
        self.name_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Campo Email
        tk.Label(self.user_frame, text="Email:").grid(
            row=2, column=0, sticky="e", pady=2
        )
        self.email_entry = tk.Entry(self.user_frame)
        self.email_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Campo Telefone
        tk.Label(self.user_frame, text="Telefone:").grid(
            row=3, column=0, sticky="e", pady=2
        )
        self.phone_entry = tk.Entry(self.user_frame)
        self.phone_entry.grid(row=3, column=1, sticky="w", pady=2)

        # Campo Status
        tk.Label(self.user_frame, text="Status:").grid(
            row=4, column=0, sticky="e", pady=2
        )
        self.status_var = tk.StringVar(value="Ativo")
        self.status_combo = ttk.Combobox(
            self.user_frame, textvariable=self.status_var, values=["Ativo", "Inativo"]
        )
        self.status_combo.grid(row=4, column=1, sticky="w", pady=2)

    def create_address_fields(self):
        """Cria os campos de endereço"""
        self.address_frame = tk.LabelFrame(
            self.main_frame, text="Endereço", padx=10, pady=5
        )
        self.address_frame.grid(
            row=1, column=1, sticky="nsew", padx=10, pady=5
        )  # Colocando à direita

        # Logradouro
        tk.Label(self.address_frame, text="Logradouro:").grid(
            row=0, column=0, sticky="e", pady=2
        )
        self.street_entry = tk.Entry(self.address_frame)
        self.street_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Número
        tk.Label(self.address_frame, text="Número:").grid(
            row=1, column=0, sticky="e", pady=2
        )
        self.number_entry = tk.Entry(self.address_frame)
        self.number_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Complemento
        tk.Label(self.address_frame, text="Complemento:").grid(
            row=2, column=0, sticky="e", pady=2
        )
        self.complement_entry = tk.Entry(self.address_frame)
        self.complement_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Bairro
        tk.Label(self.address_frame, text="Bairro:").grid(
            row=3, column=0, sticky="e", pady=2
        )
        self.district_entry = tk.Entry(self.address_frame)
        self.district_entry.grid(row=3, column=1, sticky="w", pady=2)

        # CEP
        tk.Label(self.address_frame, text="CEP:").grid(
            row=4, column=0, sticky="e", pady=2
        )
        self.cep_entry = tk.Entry(self.address_frame)
        self.cep_entry.grid(row=4, column=1, sticky="w", pady=2)

        # Cidade
        tk.Label(self.address_frame, text="Cidade:").grid(
            row=5, column=0, sticky="e", pady=2
        )
        self.city_entry = tk.Entry(self.address_frame)
        self.city_entry.grid(row=5, column=1, sticky="w", pady=2)

        # Estado
        tk.Label(self.address_frame, text="Estado (UF):").grid(
            row=6, column=0, sticky="e", pady=2
        )
        self.state_entry = tk.Entry(self.address_frame)
        self.state_entry.grid(row=6, column=1, sticky="w", pady=2)

    def create_buttons(self):
        """Cria o menu da interface"""
        # Criar menu principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Criar submenu Usuário
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Home", command=self.home_interface) # Adiciona a home

        # Cria instância da interface de emprestimos
        self.books_interface = BorrowManagementInterface(self.connection)
        self.books_interface.set_main_frame(self.main_frame)

        # Cria submenu de Empréstimos
        borrow_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Empréstimos", menu=borrow_menu)

        # Adiciona opções ao submenu Empréstimos
        borrow_menu_options = [
            ("Realizar Empréstimo", self.books_interface.borrow_interface),
            ("Devolver Livro", self.books_interface.return_interface),
            ("Buscar Empréstimos", self.books_interface.print_borrow_interface),
            ("Multas", self.books_interface.fine_interface),
            ("Reservas", self.books_interface.reserve_interface),
        ]

        for text, command in borrow_menu_options:
            borrow_menu.add_command(label=text, command=command)

        # Criar submenu Usuário
        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Usuário", menu=user_menu)

        # Adicionar opções ao submenu
        menu_options = [
            ("Criar Usuário", self.create_user_interface),
            ("Atualizar Usuário", self.update_user_interface),
            ("Deletar Usuário", self.delete_user_interface),
            ("Buscar Usuário", self.print_user_interface),
        ]

        for text, command in menu_options:
            user_menu.add_command(label=text, command=command)

        # Cria submenu de Autor
        author_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Autor", menu=author_menu)

        # Criar instância da interface de autores
        self.author_interface = AuthorManagementInterface(self.connection)
        self.author_interface.set_main_frame(self.main_frame)

        # Adicionar opções ao submenu Autor
        author_menu_options = [
            ("Criar Autor", self.author_interface.create_author_interface),
            ("Atualizar Autor", self.author_interface.update_author_interface),
            ("Buscar Autor", self.author_interface.print_author_interface),
        ]

        for text, command in author_menu_options:
            author_menu.add_command(label=text, command=command)

        # Cria instância da interface de categorias
        self.categories_interface = CategoriesManagementInterface(self.connection)
        self.categories_interface.set_main_frame(self.main_frame)

        # Cria submenu de Categorias
        categories_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Categorias", menu=categories_menu)

        # Adiciona opções ao submenu Categorias
        categories_menu_options = [
            ("Criar Categoria", self.categories_interface.create_category_interface),
            (
                "Atualizar Categoria",
                self.categories_interface.update_category_interface,
            ),
            ("Buscar Categoria", self.categories_interface.print_category_interface),
        ]

        for text, command in categories_menu_options:
            categories_menu.add_command(label=text, command=command)

        # Cria instância da interface de livros
        self.books_interface = BooksManagementInterface(self.connection)
        self.books_interface.set_main_frame(self.main_frame)

        # Cria submenu de Livros
        books_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Livros", menu=books_menu)

        # Adiciona opções ao submenu Livros
        books_menu_options = [
            ("Criar Livro", self.books_interface.create_book_interface),
            ("Atualizar Livro", self.books_interface.update_book_interface),
            ("Deletar Livro", self.books_interface.delete_book_interface),
            ("Buscar Livro", self.books_interface.print_book_interface),
        ]

        for text, command in books_menu_options:
            books_menu.add_command(label=text, command=command)



    def validate_user_data(self):
        """Valida os dados do usuário"""
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not validate_email(email):
            messagebox.showerror("Erro", "Email inválido!")
            return False

        if not validate_phone(phone):
            messagebox.showerror("Erro", "Telefone inválido! Use formato: 11912345678")
            return False

        return True

    def validate_address_data(self):
        """Valida os dados de endereço"""
        cep = self.cep_entry.get().strip()
        uf = self.state_entry.get().strip()

        if not validate_cep(cep):
            messagebox.showerror("Erro", "CEP inválido!")
            return False

        if not validate_uf(uf):
            messagebox.showerror("Erro", "UF inválida!")
            return False

        return True

    def get_user_data(self):
        """Coleta os dados do usuário dos campos"""
        return {
            "nome": self.name_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "telefone": self.phone_entry.get().strip(),
            "data_cadastro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_address_data(self):
        """Coleta os dados de endereço dos campos"""
        return {
            "logradouro": self.street_entry.get().strip(),
            "numero": self.number_entry.get().strip() or None,
            "complemento": self.complement_entry.get().strip(),
            "bairro": self.district_entry.get().strip(),
            "cep": self.cep_entry.get().strip(),
            "cidade": self.city_entry.get().strip(),
            "estado": self.state_entry.get().strip(),
        }

    def create_user_interface(self):
        """Interface para criar usuário"""
        # Limpa a área direita
        self.clear_right_frames()

        # Cria os frames de usuário e endereço
        self.create_user_fields()
        self.create_address_fields()

        # Adiciona botão de salvar
        save_frame = tk.Frame(self.main_frame)
        save_frame.grid(row=2, column=1, pady=10)

        save_button = tk.Button(
            save_frame,
            text="Salvar Usuário",
            command=self.save_user,
            **self.button_style,
        )
        save_button.pack()

    def save_user(self):
        """Salva o novo usuário"""
        if not self.validate_user_data() or not self.validate_address_data():
            return

        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = get_database_connection()
                if not self.connection:
                    messagebox.showerror(
                        "Erro", "Não foi possível conectar ao banco de dados!"
                    )
                    return

            # Criar query para inserir usuário
            user_query = create_insert_query(
                "usuarios", ["nome", "email", "telefone", "data_cadastro"]
            )

            # Coletar dados do usuário dos campos
            user_values = (
                self.name_entry.get().strip(),
                self.email_entry.get().strip(),
                self.phone_entry.get().strip(),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            # Inserir usuário
            insert_data(self.connection, user_query, user_values)

            # Criar query para inserir endereço
            address_query = create_insert_query(
                "endereco",
                [
                    "logradouro",
                    "numero",
                    "complemento",
                    "bairro",
                    "cep",
                    "cidade",
                    "estado",
                ],
            )

            # Coletar dados do endereço dos campos
            numero = self.number_entry.get().strip()
            if not numero or not numero.isdigit():
                numero = None

            address_values = (
                self.street_entry.get().strip(),
                numero,
                self.complement_entry.get().strip(),
                self.district_entry.get().strip(),
                self.cep_entry.get().strip(),
                self.city_entry.get().strip(),
                self.state_entry.get().strip(),
            )

            # Inserir endereço
            insert_data(self.connection, address_query, address_values)

            # Criar relacionamento usuário-endereço
            query = create_insert_query(
                "usuarioendereco", ["usuario_id", "endereco_id"]
            )
            values = get_usuario_id_endereco_id(self.connection)
            insert_data(self.connection, query, values)

            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
            self.clear_right_frames()  # Limpa os campos após salvar

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao criar usuário: {str(e)}")
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.commit()  # Commit das alterações

    def clear_right_frames(self):
        """Limpa os frames do lado direito da interface"""
        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["column"]) > 0:
                widget.destroy()

    def update_user_interface(self):
        """Interface para atualizar usuário"""
        self.clear_right_frames()

        # Criar frame de busca para atualização
        search_frame = tk.LabelFrame(
            self.main_frame, text="Buscar Usuário para Atualização", padx=10, pady=5
        )
        search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campos de busca
        tk.Label(search_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        id_entry = tk.Entry(search_frame)
        id_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(search_frame, text="Email:").grid(row=1, column=0, sticky="e", pady=2)
        email_entry = tk.Entry(search_frame)
        email_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Botão de busca
        search_button = tk.Button(
            search_frame,
            text="Buscar",
            command=lambda: self.perform_update(
                id_entry.get().strip(), email_entry.get().strip()
            ),
            **self.button_style,
        )
        search_button.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_user_interface(self):
        """Interface para deletar usuário"""
        self.clear_right_frames()

        # Criar frame de busca para deleção
        delete_frame = tk.LabelFrame(
            self.main_frame, text="Deletar Usuário", padx=10, pady=5
        )
        delete_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campos de busca
        tk.Label(delete_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        id_entry = tk.Entry(delete_frame)
        id_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(delete_frame, text="Email:").grid(row=1, column=0, sticky="e", pady=2)
        email_entry = tk.Entry(delete_frame)
        email_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Botão de deleção
        delete_button = tk.Button(
            delete_frame,
            text="Deletar",
            command=lambda: self.perform_delete(
                id_entry.get().strip(), email_entry.get().strip()
            ),
            **self.button_style,
        )
        delete_button.grid(row=2, column=0, columnspan=2, pady=10)

    def perform_update(self, usuario_id, email):
        """
        Executa a atualização do usuário e do endereço
        """
        if not self.connection or not self.connection.is_connected():
            print(
                f"[{datetime.datetime.now()}] Erro: Conexão com o banco de dados não disponível."
            )
            self.connection = get_database_connection()  # Tenta reconectar
            if not self.connection:
                messagebox.showerror(
                    "Erro", "Não foi possível conectar ao banco de dados!"
                )
                return False

        try:
            # Busca o usuário
            result = read_user(self.connection, usuario_id=usuario_id, email=email)

            if not result:
                messagebox.showinfo("Aviso", "Usuário não encontrado!")
                return False

            # Limpa a área direita e cria os campos de atualização
            self.clear_right_frames()

            # Cria frame para atualização
            update_frame = tk.LabelFrame(
                self.main_frame, text="Atualizar Usuário", padx=10, pady=5
            )
            update_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Preenche os campos com os dados atuais do usuário
            row = result[0]

            # Campos de usuário com seus valores atuais
            user_fields = [
                ("Nome", str(row[1]) if row[1] is not None else ""),
                ("Email", str(row[2]) if row[2] is not None else ""),
                ("Telefone", str(row[3]) if row[3] is not None else ""),
                ("Status", str(row[5]) if row[5] is not None else "Ativo"),
            ]

            user_entries = {}
            for i, (label, value) in enumerate(user_fields):
                tk.Label(update_frame, text=f"{label}:").grid(
                    row=i, column=0, sticky="e", pady=2
                )
                entry = tk.Entry(update_frame)
                entry.insert(0, value)
                entry.grid(row=i, column=1, sticky="w", pady=2)
                user_entries[label.lower()] = entry

            # Busca o endereço do usuário
            address_result = read_user_address(self.connection, usuario_id=row[0])

            if address_result and len(address_result) > 0:
                address_row = address_result[0]
                address_fields = [
                    (
                        "Logradouro",
                        str(address_row[1]) if address_row[1] is not None else "",
                    ),
                    (
                        "Número",
                        str(address_row[2]) if address_row[2] is not None else "",
                    ),
                    (
                        "Complemento",
                        str(address_row[3]) if address_row[3] is not None else "",
                    ),
                    (
                        "Bairro",
                        str(address_row[4]) if address_row[4] is not None else "",
                    ),
                    (
                        "Cidade",
                        str(address_row[5]) if address_row[5] is not None else "",
                    ),
                    (
                        "Estado",
                        str(address_row[6]) if address_row[6] is not None else "",
                    ),
                    ("CEP", str(address_row[7]) if address_row[7] is not None else ""),
                ]

                address_entries = {}
                for i, (label, value) in enumerate(
                    address_fields, start=len(user_fields)
                ):
                    tk.Label(update_frame, text=f"{label}:").grid(
                        row=i, column=0, sticky="e", pady=2
                    )
                    entry = tk.Entry(update_frame)
                    if value != "None":  # Verifica se o valor não é "None"
                        entry.insert(0, value)
                    entry.grid(row=i, column=1, sticky="w", pady=2)
                    address_entries[label.lower()] = entry
            else:
                messagebox.showinfo(
                    "Aviso", "Endereço não encontrado para este usuário!"
                )
                return False

            def save_updates():
                # Verifica se a conexão ainda está ativa
                if not self.connection or not self.connection.is_connected():
                    self.connection = get_database_connection()
                    if not self.connection:
                        messagebox.showerror(
                            "Erro", "Conexão com o banco de dados perdida!"
                        )
                        return

                try:
                    # Coleta as atualizações dos campos de usuário
                    user_updates = {}
                    if user_entries["nome"].get().strip() != str(row[1]):
                        user_updates["nome"] = user_entries["nome"].get().strip()
                    if user_entries["email"].get().strip() != str(row[2]):
                        user_updates["email"] = user_entries["email"].get().strip()
                    if user_entries["telefone"].get().strip() != str(row[3]):
                        user_updates["telefone"] = (
                            user_entries["telefone"].get().strip()
                        )
                    if user_entries["status"].get().strip() != str(row[5]):
                        user_updates["status_usuario"] = (
                            user_entries["status"].get().strip()
                        )

                    # Coleta as atualizações dos campos de endereço
                    address_updates = {}
                    if address_entries["logradouro"].get().strip() != str(
                        address_row[1]
                    ):
                        address_updates["logradouro"] = (
                            address_entries["logradouro"].get().strip()
                        )

                    # Tratamento especial para o campo número
                    numero = address_entries["número"].get().strip()
                    if numero != str(address_row[2]):
                        if not numero:  # Se estiver vazio
                            address_updates["numero"] = None
                        else:
                            # Tenta converter para número, se falhar usa 0
                            try:
                                address_updates["numero"] = int(numero)
                            except ValueError:
                                messagebox.showwarning(
                                    "Aviso",
                                    "Valor inválido para número. Será deixado em branco.",
                                )
                                address_updates["numero"] = None

                    if address_entries["complemento"].get().strip() != str(
                        address_row[3]
                    ):
                        address_updates["complemento"] = (
                            address_entries["complemento"].get().strip()
                        )
                    if address_entries["bairro"].get().strip() != str(address_row[4]):
                        address_updates["bairro"] = (
                            address_entries["bairro"].get().strip()
                        )
                    if address_entries["cidade"].get().strip() != str(address_row[5]):
                        address_updates["cidade"] = (
                            address_entries["cidade"].get().strip()
                        )
                    if address_entries["estado"].get().strip() != str(address_row[6]):
                        address_updates["estado"] = (
                            address_entries["estado"].get().strip()
                        )
                    if address_entries["cep"].get().strip() != str(address_row[7]):
                        address_updates["cep"] = address_entries["cep"].get().strip()

                    # Atualiza os dados no banco de dados
                    if user_updates:
                        user_condition = f"usuario_id = {row[0]}"
                        user_query = create_update_query(
                            "usuarios", user_updates.keys(), user_condition
                        )
                        update_data(
                            self.connection, user_query, tuple(user_updates.values())
                        )

                    if address_updates:
                        address_condition = f"endereco_id = {address_row[0]}"
                        address_query = create_update_query(
                            "endereco", address_updates.keys(), address_condition
                        )
                        update_data(
                            self.connection,
                            address_query,
                            tuple(address_updates.values()),
                        )

                    messagebox.showinfo(
                        "Sucesso", "Usuário e endereço atualizados com sucesso!"
                    )
                    self.clear_right_frames()

                except Exception as e:
                    messagebox.showerror(
                        "Erro", f"Erro ao atualizar usuário ou endereço: {str(e)}"
                    )
                    print(
                        f"[{datetime.datetime.now()}] Erro ao atualizar usuário {row[0]} ou endereço: {str(e)}"
                    )

            # Botões de ação
            buttons_frame = tk.Frame(update_frame)
            buttons_frame.grid(
                row=len(user_fields) + len(address_fields),
                column=0,
                columnspan=2,
                pady=10,
            )

            save_button = tk.Button(
                buttons_frame,
                text="Salvar Alterações",
                command=save_updates,
                **self.button_style,
            )
            save_button.pack(side=tk.LEFT, padx=5)

            cancel_button = tk.Button(
                buttons_frame,
                text="Cancelar",
                command=self.clear_right_frames,
                **self.button_style,
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preparar atualização: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao preparar atualização: {str(e)}")
            return False

    def perform_delete(self, usuario_id, email):
        """
        Executa a exclusão do usuário e seus dados relacionados
        """
        if not usuario_id and not email:
            messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
            return False

        try:

            if not self.connection or not self.connection.is_connected():
                self.connection = get_database_connection()
                if not self.connection:
                    messagebox.showerror(
                        "Erro", "Não foi possível conectar ao banco de dados!"
                    )
                    return False

            # Busca o usuário
            result = read_user(
                self.connection,
                usuario_id=usuario_id if usuario_id else None,
                email=email if email else None,
            )

            if not result:
                messagebox.showinfo("Aviso", "Usuário não encontrado!")
                return False

            # Mostra os dados do usuário e pede confirmação
            row = result[0]

            # Busca o endereço para exibição
            address_result = read_user_address(self.connection, row[0])

            if address_result:
                addr = address_result[0]
                message = f"""
                Confirma a exclusão do usuário e seus dados?

                === Dados do Usuário ===
                ID: {row[0]}
                Nome: {row[1]}
                Email: {row[2]}
                Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}
                Status: {row[5]}

                === Endereço ===
                Logradouro: {addr[1]}
                Número: {addr[2]}
                Complemento: {addr[3]}
                Bairro: {addr[4]}
                Cidade: {addr[5]}
                Estado: {addr[6]}
                CEP: {addr[7]}
                """
            else:
                message = f"""
                Confirma a exclusão do usuário?

                ID: {row[0]}
                Nome: {row[1]}
                Email: {row[2]}
                Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}
                Status: {row[5]}

                Obs: Nenhum endereço encontrado para este usuário.
                """

            if not messagebox.askyesno("Confirmar Exclusão", message):
                return False

            try:
                # Rollback any existing transaction - Garantir que não tem nenhuma transação pendente
                self.connection.rollback()

                # Inicia uma transação
                self.connection.start_transaction()

                # 1. Primeiro, obtém o endereco_id (se existir)
                if address_result:
                    endereco_id = address_result[0][0]

                    # 2. Remove a referência na tabela usuarioendereco
                    query = create_delete_query(
                        "usuarioendereco", f"usuario_id = {row[0]}"
                    )
                    delete_data(self.connection, query, None)

                    # 3. Remove o endereço
                    query = create_delete_query(
                        "endereco", f"endereco_id = {endereco_id}"
                    )
                    delete_data(self.connection, query, None)

                # 4. Finalmente, remove o usuário
                query = create_delete_query("usuarios", f"usuario_id = {row[0]}")
                delete_data(self.connection, query, None)

                # Commit da transação
                self.connection.commit()

                messagebox.showinfo(
                    "Sucesso", "Usuário e dados relacionados excluídos com sucesso!"
                )
                self.clear_right_frames()

                # Log da exclusão
                print(
                    f"[{datetime.datetime.now()}] Usuário {row[0]} ({row[1]}) e dados relacionados excluídos com sucesso."
                )
                return True

            except Exception as e:
                # Em caso de erro, faz rollback de todas as operações
                self.connection.rollback()
                messagebox.showerror("Erro", f"Erro ao excluir dados: {str(e)}")
                print(
                    f"[{datetime.datetime.now()}] Erro ao excluir dados do usuário {row[0]}: {str(e)}"
                )
                return False

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar exclusão: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao processar exclusão: {str(e)}")
            return False
        finally:
            if self.connection and self.connection.is_connected():
                self.connection.close()

    def print_user_interface(self):
        """Interface para exibir todos os usuários cadastrados"""
        self.clear_right_frames()

        # Frame principal
        main_display_frame = tk.LabelFrame(
            self.main_frame, text="Usuários Cadastrados", padx=10, pady=5
        )
        main_display_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Criar Treeview
        columns = ("ID", "Nome", "Email", "Telefone", "Data Cadastro", "Status")
        self.users_tree = ttk.Treeview(
            main_display_frame, columns=columns, show="headings", selectmode="browse"
        )

        # Configurar cabeçalhos
        for col in columns:
            self.users_tree.heading(col, text=col)
            # Ajustar largura das colunas
            if col == "Nome" or col == "Email":
                self.users_tree.column(col, width=200)
            elif col == "Data Cadastro":
                self.users_tree.column(col, width=150)
            else:
                self.users_tree.column(col, width=100)

        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(
            main_display_frame, orient="vertical", command=self.users_tree.yview
        )
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        # Posicionar elementos
        self.users_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Frame para botões
        button_frame = ttk.Frame(main_display_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Botão para atualizar lista
        ttk.Button(button_frame, text="Atualizar Lista", command=self.load_users).grid(
            row=0, column=0, padx=5
        )

        # Botão para ver detalhes
        ttk.Button(
            button_frame, text="Ver Detalhes", command=self.show_user_details
        ).grid(row=0, column=1, padx=5)

        # Configurar expansão do grid
        main_display_frame.grid_columnconfigure(0, weight=1)
        main_display_frame.grid_rowconfigure(0, weight=1)

        # Carregar usuários
        self.load_users()

    def load_users(self):
        """Carrega todos os usuários na tabela"""
        try:
            # Limpar tabela
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)

            if not self.ensure_connection():
                return

            # Buscar todos os usuários
            query = "SELECT * FROM usuarios ORDER BY usuario_id"
            result = read_data(self.connection, query)

            if result:
                for row in result:
                    # Formatar telefone
                    telefone = str(row[3])  # type: ignore
                    telefone_formatado = (
                        f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
                    )

                    # Formatar data
                    data = row[4].strftime("%d/%m/%Y %H:%M:%S") if row[4] else ""  # type: ignore

                    # Inserir na tabela
                    self.users_tree.insert(
                        "",
                        "end",
                        values=(
                            row[0],  # ID  # type: ignore
                            row[1],  # Nome # type: ignore
                            row[2],  # Email # type: ignore
                            telefone_formatado,  # Telefone formatado
                            data,  # Data formatada
                            row[5],  # Status # type: ignore
                        ),
                    )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao carregar usuários: {str(e)}")

    def show_user_details(self):
        """Mostra os detalhes do usuário selecionado"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Aviso", "Por favor, selecione um usuário para ver os detalhes."
            )
            return

        usuario_id = self.users_tree.item(selected_item)["values"][0]  # type: ignore

        try:
            if not self.ensure_connection():
                return

            # Buscar dados do usuário
            result = read_user(self.connection, usuario_id=str(usuario_id))

            if not result:
                messagebox.showinfo("Aviso", "Usuário não encontrado!")
                return

            # Criar janela de detalhes
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Detalhes do Usuário - ID: {usuario_id}")
            details_window.geometry("500x400")

            # Frame para dados do usuário
            user_frame = ttk.LabelFrame(
                details_window, text="Dados do Usuário", padding=10
            )
            user_frame.pack(fill="x", padx=10, pady=5)

            row = result[0]
            user_labels = [
                ("ID", str(row[0])),
                ("Nome", str(row[1])),
                ("Email", str(row[2])),
                (
                    "Telefone",
                    f"({str(row[3])[:2]}) {str(row[3])[2:7]}-{str(row[3])[7:]}",
                ),
                (
                    "Data de Cadastro",
                    row[4].strftime("%d/%m/%Y %H:%M:%S") if row[4] else "",
                ),
                ("Status", str(row[5])),
            ]

            for i, (label, value) in enumerate(user_labels):
                ttk.Label(user_frame, text=f"{label}:").grid(
                    row=i, column=0, sticky="e", padx=5, pady=2
                )
                ttk.Label(user_frame, text=value).grid(
                    row=i, column=1, sticky="w", padx=5, pady=2
                )

            # Buscar e exibir endereço
            address_result = read_user_address(
                self.connection, usuario_id=str(usuario_id)
            )
            if address_result:
                address_frame = ttk.LabelFrame(
                    details_window, text="Endereço", padding=10
                )
                address_frame.pack(fill="x", padx=10, pady=5)

                addr = address_result[0]
                address_labels = [
                    ("Logradouro", str(addr[1])),
                    ("Número", str(addr[2])),
                    ("Complemento", str(addr[3])),
                    ("Bairro", str(addr[4])),
                    ("Cidade", str(addr[5])),
                    ("Estado", str(addr[6])),
                    ("CEP", f"{str(addr[7])[:5]}-{str(addr[7])[5:]}"),
                ]

                for i, (label, value) in enumerate(address_labels):
                    ttk.Label(address_frame, text=f"{label}:").grid(
                        row=i, column=0, sticky="e", padx=5, pady=2
                    )
                    ttk.Label(address_frame, text=value).grid(
                        row=i, column=1, sticky="w", padx=5, pady=2
                    )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar detalhes: {str(e)}")
            print(
                f"[{datetime.datetime.now()}] Erro ao carregar detalhes do usuário {usuario_id}: {str(e)}"
            )

    def clear_fields(self):
        """Limpa os campos de entrada se eles existirem"""
        fields_to_clear = [
            "id_entry",
            "email_entry",
            "name_entry",
            "phone_entry",
            "status_entry",
            "street_entry",
            "number_entry",
            "complement_entry",
            "district_entry",
            "city_entry",
            "state_entry",
            "cep_entry",
        ]

        for field in fields_to_clear:
            if hasattr(self, field):
                entry = getattr(self, field)
                entry.delete(0, tk.END)

    def run(self):
        """Inicia o loop da interface gráfica"""
        self.root.mainloop()


def create_interface(connection=None):
    return UserManagementInterface(connection)
