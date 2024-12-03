import tkinter as tk
from tkinter import messagebox
from db_utils import (
    get_database_connection,
    update_data,
    read_data,
    create_update_query,
)
from create_user import create_insert_query, insert_data
import datetime


class AuthorManagementInterface:
    """
    Interface para gerenciamento de autores.
    Esta classe fornece uma interface gráfica para criar autores.
    """

    def __init__(self, connection=None):
        self.connection = connection
        self.author_frame = None
        self.main_frame = None
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
        print(f"Configurando main_frame: {main_frame}")  # Debug
        if not main_frame:
            raise ValueError("Frame principal não pode ser None")
        self.main_frame = main_frame
        print("Main frame configurado com sucesso!")  # Debug

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

    def create_author_fields(self):
        """Cria os campos de dados do autor"""
        self.author_frame = tk.LabelFrame(
            self.main_frame, text="Dados do Autor", padx=10, pady=5
        )
        self.author_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campo Nome
        tk.Label(self.author_frame, text="Nome:").grid(
            row=0, column=0, sticky="e", pady=2
        )
        self.name_entry = tk.Entry(self.author_frame)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Campo Nacionalidade
        tk.Label(self.author_frame, text="Nacionalidade:").grid(
            row=1, column=0, sticky="e", pady=2
        )
        self.nationality_entry = tk.Entry(self.author_frame)
        self.nationality_entry.grid(row=1, column=1, sticky="w", pady=2)

    def create_author_interface(self):
        """Interface para criar autor"""
        print("Iniciando criação da interface de autor...")  # Debug
        print(f"create_author_interface main_frame: {self.main_frame}")  # Debug

        if not self.main_frame:
            messagebox.showerror("Erro", "Frame principal não inicializado!")
            return

        try:
            self.clear_right_frames()
            self.create_author_fields()

            # Adiciona botão de salvar
            save_frame = tk.Frame(self.main_frame)
            save_frame.grid(row=2, column=1, pady=10)

            save_button = tk.Button(
                save_frame,
                text="Salvar Autor",
                command=self.save_author,
                **self.button_style,
            )
            save_button.pack()
            print("Interface de autor criada com sucesso!")  # Debug

        except Exception as e:
            print(f"Erro ao criar interface: {str(e)}")  # Debug
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def save_author(self):
        """Salva o novo autor"""
        try:
            if not self.ensure_connection():
                return

            # Criar query para inserir autor
            author_query = create_insert_query("autores", ["nome", "nacionalidade"])

            # Coletar dados do autor dos campos
            author_values = (
                self.name_entry.get().strip(),
                self.nationality_entry.get().strip(),
            )

            # Inserir autor
            insert_data(self.connection, author_query, author_values)

            messagebox.showinfo("Sucesso", "Autor criado com sucesso!")
            self.clear_right_frames()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar autor: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao criar autor: {str(e)}")

    def update_author_interface(self):
        """Interface para atualizar autor"""

        self.clear_right_frames()

        # Criar frame de busca para atualização
        search_frame = tk.LabelFrame(
            self.main_frame, text="Buscar Autor para Atualização", padx=10, pady=5
        )
        search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campos de busca
        tk.Label(search_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        id_entry = tk.Entry(search_frame)
        id_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Botão de busca
        search_button = tk.Button(
            search_frame,
            text="Buscar",
            command=lambda: self.perform_update(id_entry.get().strip()),
            **self.button_style,
        )

        search_button.grid(row=1, column=0, columnspan=2, pady=10)

    def print_author_interface(self):
        """Interface para buscar e exibir dados do autor"""
        self.clear_right_frames()

        # Criar frame de busca
        search_frame = tk.LabelFrame(
            self.main_frame, text="Buscar Autor", padx=10, pady=5
        )
        search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campos de busca
        tk.Label(search_frame, text="ID do Autor:").grid(
            row=0, column=0, sticky="e", pady=2
        )
        self.id_entry = tk.Entry(search_frame)
        self.id_entry.grid(row=0, column=1, sticky="w", pady=2)

        def perform_search():
            autor_id = self.id_entry.get().strip()
            if not autor_id:
                messagebox.showwarning("Aviso", "Por favor, informe o ID para busca!")
                return

            try:

                if not self.connection or not self.connection.is_connected():
                    self.connection = get_database_connection()

                    if not self.connection:
                        messagebox.showerror(
                            "Erro", "Não foi possível conectar ao banco de dados!"
                        )
                        return

                # Buscar dados do autor
                query = f"SELECT * FROM autores WHERE autor_id = {autor_id}"
                result = read_data(self.connection, query)

                if not result:
                    messagebox.showinfo("Aviso", "Autor não encontrado!")
                    return

                # Limpar frame atual
                self.clear_right_frames()

                # Criar novo frame para exibir resultados
                result_frame = tk.LabelFrame(
                    self.main_frame, text="Dados do Autor", padx=10, pady=5
                )
                result_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

                # Exibir dados do autor
                row = result[0]
                labels = [
                    ("ID", str(row[0])),  # type: ignore
                    ("Nome", str(row[1])),  # type: ignore
                    ("Nacionalidade", str(row[2])),  # type: ignore
                ]

                for i, (label, value) in enumerate(labels):
                    tk.Label(result_frame, text=f"{label}:").grid(
                        row=i, column=0, sticky="e", pady=2
                    )
                    tk.Label(result_frame, text=value).grid(
                        row=i, column=1, sticky="w", pady=2
                    )

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar autor: {str(e)}")

        # Botão de busca
        search_button = tk.Button(
            search_frame, text="Buscar", command=perform_search, **self.button_style
        )
        search_button.grid(row=1, column=0, columnspan=2, pady=10)

    def perform_update(self, autor_id):
        """Executa a atualização do autor"""
        if not autor_id:
            messagebox.showerror("Erro", "Informe o ID do autor!")
            return False

        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = get_database_connection()
                if not self.connection:
                    messagebox.showerror(
                        "Erro", "Não foi possível conectar ao banco de dados!"
                    )
                    return False

            # Busca o autor
            query = f"SELECT * FROM autores WHERE autor_id = {autor_id}"
            result = read_data(self.connection, query)

            if not result:
                messagebox.showinfo("Aviso", "Autor não encontrado!")
                return False

            # Limpa a área direita e cria os campos de atualização
            self.clear_right_frames()

            # Cria frame para atualização
            update_frame = tk.LabelFrame(
                self.main_frame, text="Atualizar Autor", padx=10, pady=5
            )
            update_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Preenche os campos com os dados atuais do autor
            row = result[0]

            # Campos do autor com seus valores atuais
            author_fields = [
                ("Nome", str(row[1]) if row[1] is not None else ""),  # type: ignore
                ("Nacionalidade", str(row[2]) if row[2] is not None else ""),  # type: ignore
            ]

            author_entries = {}

            for i, (label, value) in enumerate(author_fields):
                tk.Label(update_frame, text=f"{label}:").grid(
                    row=i, column=0, sticky="e", pady=2
                )

                entry = tk.Entry(update_frame)
                entry.insert(0, value)
                entry.grid(row=i, column=1, sticky="w", pady=2)
                author_entries[label.lower()] = entry

            def save_updates():
                try:
                    # Atualiza os dados no banco de dados
                    update_query = create_update_query(
                        "autores", ["nome", "nacionalidade"], f"autor_id = {autor_id}"
                    )

                    update_values = (
                        author_entries["nome"].get().strip(),
                        author_entries["nacionalidade"].get().strip(),
                    )

                    update_data(self.connection, update_query, update_values)
                    messagebox.showinfo("Sucesso", "Autor atualizado com sucesso!")
                    self.clear_right_frames()

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar autor: {str(e)}")

            # Botões de ação
            buttons_frame = tk.Frame(update_frame)
            buttons_frame.grid(row=len(author_fields), column=0, columnspan=2, pady=10)

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
            return False

    def clear_fields(self):
        """Limpa os campos de entrada se eles existirem"""
        fields_to_clear = ["name_entry", "nationality_entry"]
        for field in fields_to_clear:
            if hasattr(self, field):
                entry = getattr(self, field)
                entry.delete(0, tk.END)
