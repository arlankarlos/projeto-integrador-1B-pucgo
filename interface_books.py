import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db_utils import (
    get_database_connection,
    read_data,
    create_insert_query,
)


class BooksManagementInterface:
    """
    Interface para gerenciamento de livros.
    Permite adicionar, atualizar e gerenciar livros e seus relacionamentos.
    """

    def __init__(self, connection=None):
        self.connection = connection
        self.book_frame = None
        self.main_frame = None

        # Lista para armazenar as checkboxes dos autores
        self.author_vars = []

        # Variável para armazenar a categoria selecionada
        self.selected_category = None

        self.button_style = {
            "font": ("Arial", 11),
            "width": 20,
            "bg": "#4CAF50",
            "fg": "white",
            "relief": tk.RAISED,
            "cursor": "hand2",
        }

    def set_main_frame(self, main_frame):
        """Define o frame principal da interface"""
        if not main_frame:
            raise ValueError("Frame principal não pode ser None")
        self.main_frame = main_frame

    def clear_right_frames(self):
        """Limpa os frames do lado direito da interface"""
        if not self.main_frame:
            raise ValueError("Frame principal não foi definido.")

        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["column"]) > 0:
                widget.destroy()

    def ensure_connection(self):
        """Verifica se a conexão está ativa e tenta reconectar se necessário"""
        if not self.connection or not self.connection.is_connected():
            self.connection = get_database_connection()
            if not self.connection:
                messagebox.showerror(
                    "Erro", "Não foi possível conectar ao banco de dados!"
                )
                return False
        return True

    def create_book_interface(self):
        """Cria a interface para adicionar um novo livro"""
        try:
            self.clear_right_frames()

            # Frame principal para os dados do livro
            self.book_frame = tk.LabelFrame(
                self.main_frame, text="Dados do Livro", padx=10, pady=5
            )
            self.book_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Campos do livro
            fields = [
                ("Título:", "titulo"),
                ("ISBN:", "isbn"),
                ("Ano de Publicação:", "ano_publicacao"),
                ("Editora:", "editora"),
                ("Quantidade de Cópias:", "quantidade_copias"),
                ("Localização na Estante:", "localizacao_estante"),
            ]

            self.entries = {}
            for i, (label, field) in enumerate(fields):
                tk.Label(self.book_frame, text=label).grid(
                    row=i, column=0, sticky="e", pady=2
                )
                self.entries[field] = tk.Entry(self.book_frame)
                self.entries[field].grid(row=i, column=1, sticky="w", pady=2)

            # Frame para seleção de autores
            authors_frame = tk.LabelFrame(
                self.book_frame, text="Selecione os Autores", padx=10, pady=5
            )
            authors_frame.grid(
                row=len(fields), column=0, columnspan=2, sticky="ew", pady=5
            )

            # Buscar autores do banco
            authors = self.get_authors()
            self.author_vars = []

            # Criar canvas e scrollbar para os autores
            canvas = tk.Canvas(authors_frame, height=100)
            scrollbar = ttk.Scrollbar(
                authors_frame, orient="vertical", command=canvas.yview
            )
            scrollable_frame = tk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)

            for i, author in enumerate(authors):  # type: ignore
                var = tk.BooleanVar()
                self.author_vars.append((var, author[0]))  # type: ignore # (checkbox_var, autor_id)
                cb = tk.Checkbutton(
                    scrollable_frame,
                    text=f"{author[1]}",  # type: ignore # Nome do autor
                    variable=var,
                )
                cb.grid(row=i, column=0, sticky="w")

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Frame para seleção de categoria
            categories_frame = tk.LabelFrame(
                self.book_frame, text="Selecione a Categoria", padx=10, pady=5
            )
            categories_frame.grid(
                row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=5
            )

            # Buscar categorias do banco
            categories = self.get_categories()
            self.selected_category = tk.StringVar()

            # Criar Combobox para categorias
            category_combo = ttk.Combobox(
                categories_frame,
                textvariable=self.selected_category,
                values=[f"{cat[1]}" for cat in categories],  # type: ignore
                state="readonly",
            )
            category_combo.grid(row=0, column=0, pady=5)

            # Armazenar o mapeamento de nomes para IDs
            self.category_map = {cat[1]: cat[0] for cat in categories}  # type: ignore

            # Botão Salvar
            tk.Button(
                self.book_frame,
                text="Salvar Livro",
                command=self.save_book,
                **self.button_style,
            ).grid(row=len(fields) + 2, column=0, columnspan=2, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def get_authors(self):
        """Busca todos os autores do banco de dados"""
        try:
            query = "SELECT autor_id, nome FROM autores ORDER BY nome"
            return read_data(self.connection, query)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar autores: {str(e)}")
            return []

    def get_categories(self):
        """Busca todas as categorias do banco de dados"""
        try:
            query = "SELECT categoria_id, nome FROM categorias ORDER BY nome"
            return read_data(self.connection, query)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar categorias: {str(e)}")
            return []

    def save_book(self):
        """Salva o livro e seus relacionamentos no banco de dados"""
        try:
            if not self.validate_fields():
                return

            # Coletar dados do formulário
            book_data = {
                "titulo": self.entries["titulo"].get().strip(),
                "isbn": self.entries["isbn"].get().strip(),
                "ano_publicacao": int(self.entries["ano_publicacao"].get().strip()),
                "editora": self.entries["editora"].get().strip(),
                "quantidade_copias": int(
                    self.entries["quantidade_copias"].get().strip()
                ),
                "localizacao_estante": self.entries["localizacao_estante"]
                .get()
                .strip(),
            }

            # Iniciar transação
            self.connection.rollback()  # type: ignore
            self.connection.start_transaction()  # type: ignore

            try:
                cursor = self.connection.cursor()  # type: ignore

                # Inserir livro
                book_query = create_insert_query("livros", book_data.keys())
                cursor.execute(book_query, tuple(book_data.values()))

                # Obter o ID do livro inserido
                cursor.execute("SELECT LAST_INSERT_ID()")
                livro_id = cursor.fetchone()[0]  # type: ignore

                # print(f"livro_id após inserção: {livro_id}")  # Debugging

                if livro_id is None:
                    raise Exception("Erro ao obter livro_id após inserção.")

                # Inserir relacionamentos com autores
                selected_authors = [
                    author_id for var, author_id in self.author_vars if var.get()
                ]

                for author_id in selected_authors:
                    author_query = (
                        "INSERT INTO livrosautores (livro_id, autor_id) VALUES (%s, %s)"
                    )
                    # print(
                    #     f"Inserindo autor - livro_id: {livro_id}, author_id: {author_id}"
                    # )
                    cursor.execute(author_query, (livro_id, author_id))  # type: ignore

                # Inserir relacionamento com categoria
                category_name = self.selected_category.get()  # type: ignore
                if category_name in self.category_map:
                    category_id = self.category_map[category_name]
                    category_query = "INSERT INTO livroscategorias (livro_id, categoria_id) VALUES (%s, %s)"
                    # print(
                    #     f"Inserindo categoria - livro_id: {livro_id}, category_id: {category_id}"
                    # )
                    cursor.execute(category_query, (livro_id, category_id))  # type: ignore

                # Commit da transação
                self.connection.commit()  # type: ignore
                cursor.close()

                messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
                self.clear_fields()

            except Exception as e:
                self.connection.rollback()  # type: ignore
                if "cursor" in locals():
                    cursor.close()  # type: ignore
                raise e

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar livro: {str(e)}")

    def validate_fields(self):
        """Valida os campos do formulário"""
        try:
            # Verificar campos obrigatórios
            for field, entry in self.entries.items():
                if not entry.get().strip():
                    messagebox.showwarning("Aviso", f"O campo {field} é obrigatório!")
                    return False

            # Validar campos numéricos
            try:
                int(self.entries["ano_publicacao"].get().strip())
                int(self.entries["quantidade_copias"].get().strip())
            except ValueError:
                messagebox.showwarning(
                    "Aviso",
                    "Ano de publicação e quantidade de cópias devem ser números inteiros!",
                )
                return False

            # Verificar se pelo menos um autor foi selecionado
            if not any(var.get() for var, _ in self.author_vars):
                messagebox.showwarning("Aviso", "Selecione pelo menos um autor!")
                return False

            # Verificar se uma categoria foi selecionada
            if not self.selected_category.get():  # type: ignore
                messagebox.showwarning("Aviso", "Selecione uma categoria!")
                return False

            return True

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na validação: {str(e)}")
            return False

    def update_book_interface(self):
        """Cria a interface para atualizar um livro existente"""
        try:
            self.clear_right_frames()

            # Frame principal para atualização
            self.book_frame = tk.LabelFrame(
                self.main_frame, text="Atualizar Livro", padx=10, pady=5
            )
            self.book_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para busca do livro
            search_frame = tk.LabelFrame(
                self.book_frame, text="Buscar Livro", padx=10, pady=5
            )
            search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

            # Opções de busca
            self.search_type = tk.StringVar(value="titulo")
            search_options = [
                ("Título", "titulo"),
                ("ISBN", "isbn"),
                ("ID", "livro_id")
            ]

            for i, (text, value) in enumerate(search_options):
                tk.Radiobutton(
                    search_frame,
                    text=text,
                    variable=self.search_type,
                    value=value
                ).grid(row=0, column=i, padx=5)

            # Campo de busca
            self.search_entry = tk.Entry(search_frame, width=40)
            self.search_entry.grid(row=1, column=0, columnspan=2, pady=5)

            # Botão de busca
            tk.Button(
                search_frame,
                text="Buscar",
                command=self.search_book,
                **self.button_style
            ).grid(row=1, column=2, padx=5)

            # Frame para os dados do livro (inicialmente vazio)
            self.update_frame = tk.LabelFrame(
                self.book_frame, text="Dados do Livro", padx=10, pady=5
            )
            self.update_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface de atualização: {str(e)}")

    def search_book(self):
        """Busca um livro com base no critério selecionado"""
        try:
            search_value = self.search_entry.get().strip()
            search_type = self.search_type.get()

            if not search_value:
                messagebox.showwarning("Aviso", "Digite um valor para busca!")
                return

            # Construir query de busca
            query = """
                SELECT 
                    l.livro_id, 
                    l.titulo, 
                    l.isbn, 
                    l.ano_publicacao, 
                    l.editora, 
                    l.quantidade_copias, 
                    l.localizacao_estante,
                    GROUP_CONCAT(DISTINCT a.autor_id) AS autor_ids,
                    GROUP_CONCAT(DISTINCT a.nome) AS autor_names,
                    MAX(c.categoria_id) AS categoria_id, 
                    MAX(c.nome) AS categoria_nome
                FROM livros l
                LEFT JOIN livrosautores la ON l.livro_id = la.livro_id
                LEFT JOIN autores a ON la.autor_id = a.autor_id
                LEFT JOIN livroscategorias lc ON l.livro_id = lc.livro_id
                LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
                WHERE l.{} = %s
                GROUP BY l.livro_id, l.titulo, l.isbn, l.ano_publicacao, l.editora, 
                        l.quantidade_copias, l.localizacao_estante
            """.format(search_type)

            cursor = self.connection.cursor(dictionary=True) # type: ignore
            cursor.execute(query, (search_value,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                messagebox.showwarning("Aviso", "Livro não encontrado!")
                return

            self.load_book_data(result)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar livro: {str(e)}")

    def load_book_data(self, book_data):
        """Carrega os dados do livro no formulário de atualização"""
        try:
            # Limpar frame de atualização
            for widget in self.update_frame.winfo_children():
                widget.destroy()

            # Armazenar ID do livro
            self.current_book_id = book_data['livro_id']

            # Campos do livro
            fields = [
                ("Título:", "titulo"),
                ("ISBN:", "isbn"),
                ("Ano de Publicação:", "ano_publicacao"),
                ("Editora:", "editora"),
                ("Quantidade de Cópias:", "quantidade_copias"),
                ("Localização na Estante:", "localizacao_estante"),
            ]

            self.update_entries = {}
            for i, (label, field) in enumerate(fields):
                tk.Label(self.update_frame, text=label).grid(
                    row=i, column=0, sticky="e", pady=2
                )
                self.update_entries[field] = tk.Entry(self.update_frame)
                self.update_entries[field].insert(0, str(book_data[field]))
                self.update_entries[field].grid(row=i, column=1, sticky="w", pady=2)

            # Frame para seleção de autores
            self.load_authors_selection(book_data)

            # Frame para seleção de categoria
            self.load_category_selection(book_data)

            # Botão Salvar Alterações
            tk.Button(
                self.update_frame,
                text="Salvar Alterações",
                command=self.save_book_updates,
                **self.button_style
            ).grid(row=len(fields) + 3, column=0, columnspan=2, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do livro: {str(e)}")

    def load_authors_selection(self, book_data):
        """Carrega a seleção de autores para o livro"""
        authors_frame = tk.LabelFrame(
            self.update_frame, text="Selecione os Autores", padx=10, pady=5
        )
        authors_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        # Buscar todos os autores
        authors = self.get_authors()
        self.author_vars = []

        # Criar canvas e scrollbar
        canvas = tk.Canvas(authors_frame, height=100)
        scrollbar = ttk.Scrollbar(authors_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Lista de autores do livro
        current_authors = []
        if book_data.get('autor_ids'):
            current_authors = [str(aid) for aid in book_data['autor_ids'].split(',')]

        for i, author in enumerate(authors): # type: ignore
            var = tk.BooleanVar()
            self.author_vars.append((var, author[0])) # type: ignore

            # Marcar autores já associados ao livro
            if str(author[0]) in current_authors: # type: ignore
                var.set(True)

            cb = tk.Checkbutton(
                scrollable_frame,
                text=f"{author[1]}", # type: ignore
                variable=var
            )
            cb.grid(row=i, column=0, sticky="w")

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_category_selection(self, book_data):
        """Carrega a seleção de categoria para o livro"""
        categories_frame = tk.LabelFrame(
            self.update_frame, text="Selecione a Categoria", padx=10, pady=5
        )
        categories_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)

        # Buscar categorias
        categories = self.get_categories()
        self.selected_category = tk.StringVar()

        # Criar Combobox
        category_combo = ttk.Combobox(
            categories_frame,
            textvariable=self.selected_category,
            values=[f"{cat[1]}" for cat in categories], # type: ignore
            state="readonly"
        )
        category_combo.grid(row=0, column=0, pady=5)

        # Armazenar mapeamento e selecionar categoria atual
        self.category_map = {cat[1]: cat[0] for cat in categories} # type: ignore
        if book_data.get('categoria_nome'):
            self.selected_category.set(book_data['categoria_nome'])

    def save_book_updates(self):
        """Salva as alterações feitas no livro"""
        try:
            if not self.validate_book_update():
                return

            # Coletar dados atualizados
            book_data = {
                'titulo': self.update_entries['titulo'].get().strip(),
                'isbn': self.update_entries['isbn'].get().strip(),
                'ano_publicacao': int(self.update_entries['ano_publicacao'].get().strip()),
                'editora': self.update_entries['editora'].get().strip(),
                'quantidade_copias': int(self.update_entries['quantidade_copias'].get().strip()),
                'localizacao_estante': self.update_entries['localizacao_estante'].get().strip()
            }

            # Iniciar transação
            self.connection.rollback() # type: ignore
            self.connection.start_transaction() # type: ignore
            cursor = self.connection.cursor() # type: ignore

            try:
                # Atualizar dados do livro
                update_query = """
                    UPDATE livros 
                    SET titulo=%s, isbn=%s, ano_publicacao=%s, 
                        editora=%s, quantidade_copias=%s, localizacao_estante=%s
                    WHERE livro_id=%s
                """
                values = (*book_data.values(), self.current_book_id)
                cursor.execute(update_query, values)

                # Atualizar autores
                cursor.execute("DELETE FROM livrosautores WHERE livro_id=%s", 
                            (self.current_book_id,))

                selected_authors = [
                    author_id for var, author_id in self.author_vars if var.get()
                ]

                for author_id in selected_authors:
                    cursor.execute(
                        "INSERT INTO livrosautores (livro_id, autor_id) VALUES (%s, %s)",
                        (self.current_book_id, author_id)
                    )

                # Atualizar categoria
                cursor.execute("DELETE FROM livroscategorias WHERE livro_id=%s", 
                            (self.current_book_id,))

                category_name = self.selected_category.get() # type: ignore
                if category_name in self.category_map:
                    category_id = self.category_map[category_name]
                    cursor.execute(
                        "INSERT INTO livroscategorias (livro_id, categoria_id) VALUES (%s, %s)",
                        (self.current_book_id, category_id) # type: ignore
                    )

                self.connection.commit() # type: ignore
                messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")

            except Exception as e:
                self.connection.rollback() # type: ignore
                raise e
            finally:
                cursor.close()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar livro: {str(e)}")

    def validate_book_update(self):
        """Valida os campos antes de atualizar o livro"""
        try:
            # Verificar campos obrigatórios
            for field, entry in self.update_entries.items():
                if not entry.get().strip():
                    messagebox.showwarning("Aviso", f"O campo {field} é obrigatório!")
                    return False

            # Validar campos numéricos
            try:
                int(self.update_entries['ano_publicacao'].get().strip())
                int(self.update_entries['quantidade_copias'].get().strip())
            except ValueError:
                messagebox.showwarning(
                    "Aviso",
                    "Ano de publicação e quantidade de cópias devem ser números inteiros!"
                )
                return False

            # Verificar se pelo menos um autor foi selecionado
            if not any(var.get() for var, _ in self.author_vars):
                messagebox.showwarning("Aviso", "Selecione pelo menos um autor!")
                return False

            # Verificar se uma categoria foi selecionada
            if not self.selected_category.get(): # type: ignore
                messagebox.showwarning("Aviso", "Selecione uma categoria!")
                return False

            return True

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na validação: {str(e)}")
            return False

    def delete_book_interface(self):
        """Cria a interface para deletar um livro existente"""
        try:
            self.clear_right_frames()

            # Frame principal para deleção
            self.delete_frame = tk.LabelFrame(
                self.main_frame, text="Deletar Livro", padx=10, pady=5
            )
            self.delete_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para busca do livro
            search_frame = tk.LabelFrame(
                self.delete_frame, text="Buscar Livro", padx=10, pady=5
            )
            search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

            # Opções de busca
            self.search_type = tk.StringVar(value="titulo")
            search_options = [
                ("Título", "titulo"),
                ("ISBN", "isbn"),
                ("ID", "livro_id")
            ]

            for i, (text, value) in enumerate(search_options):
                tk.Radiobutton(
                    search_frame,
                    text=text,
                    variable=self.search_type,
                    value=value
                ).grid(row=0, column=i, padx=5)

            # Campo de busca
            self.search_entry = tk.Entry(search_frame, width=40)
            self.search_entry.grid(row=1, column=0, columnspan=2, pady=5)

            # Botão de busca
            tk.Button(
                search_frame,
                text="Buscar",
                command=self.search_book_for_deletion,
                **self.button_style
            ).grid(row=1, column=2, padx=5)

            # Frame para exibir informações do livro (inicialmente vazio)
            self.book_info_frame = tk.LabelFrame(
                self.delete_frame, text="Informações do Livro", padx=10, pady=5
            )
            self.book_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface de deleção: {str(e)}")

    def search_book_for_deletion(self):
        """Busca um livro para deleção e exibe suas informações"""
        try:
            search_value = self.search_entry.get().strip()
            search_type = self.search_type.get()

            if not search_value:
                messagebox.showwarning("Aviso", "Digite um valor para busca!")
                return

            # Construir query de busca
            query = """
                SELECT 
                    l.livro_id, 
                    l.titulo, 
                    l.isbn, 
                    l.ano_publicacao, 
                    l.editora, 
                    l.quantidade_copias, 
                    l.localizacao_estante,
                    GROUP_CONCAT(DISTINCT a.nome SEPARATOR ', ') AS autores,
                    MAX(c.nome) AS categoria
                FROM livros l
                LEFT JOIN livrosautores la ON l.livro_id = la.livro_id
                LEFT JOIN autores a ON la.autor_id = a.autor_id
                LEFT JOIN livroscategorias lc ON l.livro_id = lc.livro_id
                LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
                WHERE l.{} = %s
                GROUP BY l.livro_id, l.titulo, l.isbn, l.ano_publicacao, 
                        l.editora, l.quantidade_copias, l.localizacao_estante
            """.format(search_type)

            cursor = self.connection.cursor(dictionary=True) # type: ignore
            cursor.execute(query, (search_value,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                messagebox.showwarning("Aviso", "Livro não encontrado!")
                return

            self.display_book_info_for_deletion(result)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar livro: {str(e)}")

    def display_book_info_for_deletion(self, book_data):
        """Exibe as informações do livro e botão de deleção"""
        try:
            # Limpar frame de informações
            for widget in self.book_info_frame.winfo_children():
                widget.destroy()

            # Armazenar ID do livro
            self.book_to_delete = book_data['livro_id']

            # Criar labels com informações do livro
            info_text = f"""
            Título: {book_data['titulo']}
            ISBN: {book_data['isbn']}
            Ano de Publicação: {book_data['ano_publicacao']}
            Editora: {book_data['editora']}
            Quantidade de Cópias: {book_data['quantidade_copias']}
            Localização na Estante: {book_data['localizacao_estante']}
            Autores: {book_data['autores'] if book_data['autores'] else 'Nenhum'}
            Categoria: {book_data['categoria'] if book_data['categoria'] else 'Nenhuma'}
            """

            tk.Label(
                self.book_info_frame,
                text=info_text,
                justify=tk.LEFT,
                padx=10,
                pady=5
            ).pack()

            # Criar um estilo específico para o botão de deletar
            delete_button_style = self.button_style.copy()  # Copia o estilo base
            delete_button_style.update({
                'bg': 'red',
                'fg': 'white'
            })

            # Botão para deletar
            tk.Button(
                self.book_info_frame,
                text="Apagar Livro",
                command=self.confirm_deletion,
                **delete_button_style
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exibir informações do livro: {str(e)}")

    def confirm_deletion(self):
        """Solicita confirmação do usuário antes de deletar o livro"""
        if messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja apagar este livro?\nEsta ação não pode ser desfeita!"
        ):
            self.delete_book_from_database()

    def delete_book_from_database(self):
        """Remove o livro e seus relacionamentos do banco de dados"""
        try:
            cursor = self.connection.cursor() # type: ignore
            self.connection.rollback() # type: ignore
            self.connection.start_transaction() # type: ignore

            try:
                # Remover relacionamentos com autores
                cursor.execute(
                    "DELETE FROM livrosautores WHERE livro_id = %s",
                    (self.book_to_delete,)
                )

                # Remover relacionamentos com categorias
                cursor.execute(
                    "DELETE FROM livroscategorias WHERE livro_id = %s",
                    (self.book_to_delete,)
                )

                # Remover o livro
                cursor.execute(
                    "DELETE FROM livros WHERE livro_id = %s",
                    (self.book_to_delete,)
                )

                self.connection.commit() # type: ignore
                messagebox.showinfo("Sucesso", "Livro deletado com sucesso!")

                # Limpar a interface
                self.search_entry.delete(0, tk.END)
                for widget in self.book_info_frame.winfo_children():
                    widget.destroy()

            except Exception as e:
                self.connection.rollback() # type: ignore
                raise e
            finally:
                cursor.close()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar livro: {str(e)}")

    def print_book_interface(self):
        """Cria a interface para exibir os livros armazenados no banco de dados"""
        try:
            self.clear_right_frames()

            # Frame principal para exibição
            self.print_frame = tk.LabelFrame(
                self.main_frame, text="Livros Disponíveis", padx=10, pady=5
            )
            self.print_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Campo de busca
            search_frame = tk.Frame(self.print_frame)
            search_frame.grid(row=0, column=0, sticky="ew", pady=5)

            tk.Label(search_frame, text="Buscar:").grid(row=0, column=0, padx=5)
            self.search_entry = tk.Entry(search_frame, width=40)
            self.search_entry.grid(row=0, column=1, padx=5)
            self.search_entry.bind("<KeyRelease>", lambda event: self.filter_books())

            # Botão para exportar para CSV
            tk.Button(
                search_frame,
                text="Exportar para CSV",
                command=self.export_to_csv,
                **self.button_style
            ).grid(row=0, column=2, padx=5)

            # Frame para tabela de exibição
            self.table_frame = tk.Frame(self.print_frame)
            self.table_frame.grid(row=1, column=0, sticky="nsew", pady=5)

            # Configurar tabela
            self.book_table = ttk.Treeview(
                self.table_frame,
                columns=(
                    "ID", "Título", "ISBN", "Ano", "Editora", "Cópias", "Estante", "Categoria", "Autores"
                ),
                show="headings",
                height=15
            )
            self.book_table.grid(row=0, column=0, sticky="nsew")

            # Configurar colunas
            self.book_table.heading("ID", text="ID")
            self.book_table.heading("Título", text="Título")
            self.book_table.heading("ISBN", text="ISBN")
            self.book_table.heading("Ano", text="Ano")
            self.book_table.heading("Editora", text="Editora")
            self.book_table.heading("Cópias", text="Cópias")
            self.book_table.heading("Estante", text="Estante")
            self.book_table.heading("Categoria", text="Categoria")
            self.book_table.heading("Autores", text="Autores")

            # Ajustar largura das colunas
            self.book_table.column("ID", width=50, anchor="center")
            self.book_table.column("Título", width=200, anchor="w")
            self.book_table.column("ISBN", width=100, anchor="center")
            self.book_table.column("Ano", width=80, anchor="center")
            self.book_table.column("Editora", width=150, anchor="w")
            self.book_table.column("Cópias", width=80, anchor="center")
            self.book_table.column("Estante", width=100, anchor="w")
            self.book_table.column("Categoria", width=150, anchor="w")
            self.book_table.column("Autores", width=200, anchor="w")

            # Scrollbar para a tabela
            scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.book_table.yview)
            self.book_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky="ns")

            # Carregar dados do banco de dados
            self.fetch_books_from_database()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface de exibição: {str(e)}")

    def fetch_books_from_database(self):
        """Busca os dados dos livros no banco de dados e exibe na tabela"""
        try:
            query = """
                SELECT 
                    l.livro_id, 
                    l.titulo, 
                    l.isbn, 
                    l.ano_publicacao, 
                    l.editora, 
                    l.quantidade_copias, 
                    l.localizacao_estante,
                    GROUP_CONCAT(DISTINCT a.nome SEPARATOR ', ') AS autores,
                    MAX(c.nome) AS categoria
                FROM livros l
                LEFT JOIN livrosautores la ON l.livro_id = la.livro_id
                LEFT JOIN autores a ON la.autor_id = a.autor_id
                LEFT JOIN livroscategorias lc ON l.livro_id = lc.livro_id
                LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
                GROUP BY 
                    l.livro_id, 
                    l.titulo, 
                    l.isbn, 
                    l.ano_publicacao, 
                    l.editora, 
                    l.quantidade_copias, 
                    l.localizacao_estante;
            """
            connection = get_database_connection()
            if not connection:
                raise Exception("Não foi possível conectar ao banco de dados.")

            books = read_data(connection, query)
            if not books:  # Se não houver resultados, inicializar como lista vazia
                books = []

            # Limpar tabela antes de carregar novos dados
            for row in self.book_table.get_children():
                self.book_table.delete(row)

            # Inserir dados na tabela
            for book in books:
                self.book_table.insert(
                    "",
                    "end",
                    values=(
                        book[0],  # ID # type: ignore
                        book[1],  # Título # type: ignore
                        book[2],  # ISBN # type: ignore
                        book[3],  # Ano de Publicação # type: ignore
                        book[4],  # Editora # type: ignore
                        book[5],  # Quantidade de Cópias # type: ignore
                        book[6],  # Localização na Estante # type: ignore
                        book[8] if book[8] else "Sem Categoria",  # Categoria # type: ignore
                        book[7] if book[7] else "Sem Autores"  # Autores # type: ignore
                    )
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados dos livros: {str(e)}")

    def filter_books(self):
        """Filtra os livros exibidos na tabela com base no texto de busca"""
        try:
            search_text = self.search_entry.get().strip().lower()

            # Se o campo de busca estiver vazio, recarregar todos os dados
            if not search_text:
                self.fetch_books_from_database()
                return

            # Filtrar os resultados na tabela
            for row in self.book_table.get_children():
                values = self.book_table.item(row, "values")
                if any(search_text in str(value).lower() for value in values):
                    self.book_table.reattach(row, '', 'end')  # type: ignore # Reexibe a linha 
                else:
                    self.book_table.detach(row)  # Oculta a linha

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar livros: {str(e)}")

    def export_to_csv(self):
        """Exporta os dados exibidos na tabela para um arquivo CSV"""
        try:
            # Abrir diálogo para salvar arquivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Salvar como"
            )
            if not filename:
                return

            # Obter dados da tabela
            rows = [self.book_table.item(row, "values") for row in self.book_table.get_children()]

            # Escrever dados no arquivo CSV
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                # Cabeçalhos
                writer.writerow(["ID", "Título", "ISBN", "Ano", "Editora", "Cópias", "Estante", "Categoria", "Autores"])
                # Dados
                writer.writerows(rows)

            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados para CSV: {str(e)}")

    def clear_fields(self):
        """Limpa todos os campos do formulário"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        # Limpar seleção de autores
        for var, _ in self.author_vars:
            var.set(False)

        # Limpar seleção de categoria
        self.selected_category.set("")  # type: ignore
