import tkinter as tk
from tkinter import ttk, messagebox
from db_utils import (
    get_database_connection,
    update_data,
    read_data,
    insert_data,
    create_insert_query,
)
from datetime import datetime

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
            scrollbar = ttk.Scrollbar(authors_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)

            for i, author in enumerate(authors):
                var = tk.BooleanVar()
                self.author_vars.append((var, author[0]))  # (checkbox_var, autor_id)
                cb = tk.Checkbutton(
                    scrollable_frame,
                    text=f"{author[1]}",  # Nome do autor
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
                values=[f"{cat[1]}" for cat in categories],  # Nome da categoria
                state="readonly"
            )
            category_combo.grid(row=0, column=0, pady=5)

            # Armazenar o mapeamento de nomes para IDs
            self.category_map = {cat[1]: cat[0] for cat in categories}

            # Botão Salvar
            tk.Button(
                self.book_frame,
                text="Salvar Livro",
                command=self.save_book,
                **self.button_style
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
                'titulo': self.entries['titulo'].get().strip(),
                'isbn': self.entries['isbn'].get().strip(),
                'ano_publicacao': int(self.entries['ano_publicacao'].get().strip()),
                'editora': self.entries['editora'].get().strip(),
                'quantidade_copias': int(self.entries['quantidade_copias'].get().strip()),
                'localizacao_estante': self.entries['localizacao_estante'].get().strip()
            }

            # Iniciar transação
            self.connection.rollback()
            self.connection.start_transaction()

            try:
                # Inserir livro
                book_query = create_insert_query("livros", book_data.keys())
                insert_data(self.connection, book_query, tuple(book_data.values()))

                # Obter o ID do livro inserido
                livro_id = self.connection.cursor().lastrowid

                # Inserir relacionamentos com autores
                selected_authors = [
                    author_id for var, author_id in self.author_vars if var.get()
                ]

                for author_id in selected_authors:
                    author_query = create_insert_query(
                        "livrosautores", ["livro_id", "autor_id"]
                    )
                    insert_data(self.connection, author_query, (livro_id, author_id))

                # Inserir relacionamento com categoria
                category_name = self.selected_category.get()
                if category_name in self.category_map:
                    category_id = self.category_map[category_name]
                    category_query = create_insert_query(
                        "livroscategorias", ["livro_id", "categoria_id"]
                    )
                    insert_data(self.connection, category_query, (livro_id, category_id))

                # Commit da transação
                self.connection.commit()
                messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
                self.clear_fields()

            except Exception as e:
                self.connection.rollback()
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
                int(self.entries['ano_publicacao'].get().strip())
                int(self.entries['quantidade_copias'].get().strip())
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
            if not self.selected_category.get():
                messagebox.showwarning("Aviso", "Selecione uma categoria!")
                return False

            return True

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na validação: {str(e)}")
            return False

    def clear_fields(self):
        """Limpa todos os campos do formulário"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        # Limpar seleção de autores
        for var, _ in self.author_vars:
            var.set(False)

        # Limpar seleção de categoria
        self.selected_category.set('')