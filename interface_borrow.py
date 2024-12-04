import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from db_utils import (
    get_database_connection,
    create_insert_query,
    insert_data,
    read_data,
    update_data,
)


class BorrowManagementInterface:
    """
    Interface para gerenciamento de empréstimos.
    Esta classe fornece uma interface gráfica para criar e gerenciar empréstimos.
    """

    def __init__(self, connection=None):
        self.connection = connection
        self.borrow_frame = None
        self.main_frame = None
        self.book_combobox = None
        self.user_combobox = None
        self.return_date_entry = None
        self.books_data = []
        self.users_data = []
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

    def fetch_available_books(self):
        """Recupera livros disponíveis do banco de dados"""
        if self.ensure_connection():
            query = """
                SELECT livro_id, titulo, quantidade_copias 
                FROM livros 
                WHERE quantidade_copias > 0
            """
            return read_data(self.connection, query)
        return []

    def fetch_users(self):
        """Recupera usuários registrados do banco de dados"""
        if self.ensure_connection():
            query = "SELECT usuario_id, nome FROM usuarios"
            return read_data(self.connection, query)
        return []

    def create_loan_entry(self, book_id, user_id, return_date):
        """Cria um novo empréstimo no banco de dados"""
        try:
            if not self.ensure_connection():
                return False

            # Inserir empréstimo
            columns = [
                "livro_id",
                "usuario_id",
                "data_emprestimo",
                "data_devolucao_prevista",
                "status_emprestimo",
            ]
            query = create_insert_query("emprestimos", columns)
            values = (book_id, user_id, datetime.now().date(), return_date, "Ativo")
            insert_data(self.connection, query, values)

            # Atualizar quantidade de livros
            update_query = """
                UPDATE livros 
                SET quantidade_copias = quantidade_copias - 1 
                WHERE livro_id = %s
            """
            insert_data(self.connection, update_query, (book_id,))

            self.connection.commit()  # type: ignore
            return True
        except Exception as e:
            print(f"Erro ao criar empréstimo: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def confirm_loan(self):
        """Confirma o empréstimo após validações"""
        try:
            book_index = self.book_combobox.current()  # type: ignore
            user_index = self.user_combobox.current()  # type: ignore

            if book_index < 0 or user_index < 0:
                messagebox.showerror("Erro", "Selecione um livro e um usuário")
                return

            book_id = self.books_data[book_index][0]  # type: ignore
            user_id = self.users_data[user_index][0]  # type: ignore
            return_date = self.return_date_entry.get_date()  # type: ignore

            if self.create_loan_entry(book_id, user_id, return_date):
                messagebox.showinfo("Sucesso", "Empréstimo realizado com sucesso!")
                self.clear_right_frames()
            else:
                messagebox.showerror("Erro", "Falha ao realizar empréstimo")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar empréstimo: {str(e)}")

    def borrow_interface(self):
        """Interface principal para empréstimo de livros"""
        try:
            print("Iniciando criação da interface de empréstimo...")  # Debug
            if not self.main_frame:
                messagebox.showerror("Erro", "Frame principal não inicializado!")
                return

            self.clear_right_frames()

            # Frame principal do empréstimo
            self.borrow_frame = tk.LabelFrame(
                self.main_frame, text="Novo Empréstimo", padx=10, pady=5
            )
            self.borrow_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Carregar dados
            self.books_data = self.fetch_available_books()
            self.users_data = self.fetch_users()

            # Livros disponíveis
            tk.Label(self.borrow_frame, text="Livro:").grid(
                row=0, column=0, pady=5, sticky=tk.W
            )
            self.book_combobox = ttk.Combobox(self.borrow_frame, width=40)
            self.book_combobox["values"] = [
                f"{book[1]} (Disponível: {book[2]})"  # type: ignore
                for book in self.books_data  # type: ignore
            ]  # type: ignore
            self.book_combobox.grid(row=1, column=0, pady=5)

            # Usuários
            tk.Label(self.borrow_frame, text="Usuário:").grid(
                row=2, column=0, pady=5, sticky=tk.W
            )
            self.user_combobox = ttk.Combobox(self.borrow_frame, width=40)
            self.user_combobox["values"] = [user[1] for user in self.users_data]  # type: ignore
            self.user_combobox.grid(row=3, column=0, pady=5)

            # Data de devolução prevista
            tk.Label(self.borrow_frame, text="Data de Devolução Prevista:").grid(
                row=4, column=0, pady=5, sticky=tk.W
            )
            self.return_date_entry = DateEntry(
                self.borrow_frame,
                width=20,
                date_pattern="yyyy-mm-dd",
                mindate=datetime.now().date(),
                maxdate=datetime.now().date() + timedelta(days=30),
            )
            self.return_date_entry.set_date(datetime.now().date() + timedelta(days=14))
            self.return_date_entry.grid(row=5, column=0, pady=5)

            # Botão confirmar
            tk.Button(
                self.borrow_frame,
                text="Confirmar Empréstimo",
                command=self.confirm_loan,
                **self.button_style,
            ).grid(row=6, column=0, pady=20)

            print("Interface de empréstimo criada com sucesso!")  # Debug

        except Exception as e:
            print(f"Erro ao criar interface: {str(e)}")  # Debug
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def fetch_active_loans(self, usuario_id):
        """Recupera os empréstimos ativos de um usuário"""
        if self.ensure_connection():
            query = f"""
                SELECT e.emprestimo_id, e.livro_id, l.titulo, 
                    e.data_emprestimo, e.data_devolucao_prevista
                FROM emprestimos e
                JOIN livros l ON e.livro_id = l.livro_id
                WHERE e.usuario_id = {int(usuario_id)} 
                AND e.status_emprestimo = 'Ativo'
            """
            return read_data(self.connection, query)
        return []

    def update_loan_status(self, emprestimo_id):
        """Atualiza o status do empréstimo para Devolvido"""
        if self.ensure_connection():
            try:
                emprestimo_id = int(emprestimo_id)  # Garantir que é um inteiro
                current_date = datetime.now().date()

                # Atualizar empréstimo
                update_query = f"""
                    UPDATE emprestimos 
                    SET status_emprestimo = 'Devolvido',
                        data_devolucao_real = '{current_date}'
                    WHERE emprestimo_id = {emprestimo_id}
                """
                update_data(self.connection, update_query, None)

                # Recuperar livro_id
                query = f"SELECT livro_id FROM emprestimos WHERE emprestimo_id = {emprestimo_id}"
                result = read_data(self.connection, query)
                if result:
                    livro_id = int(result[0][0])  # type: ignore # Garantir que é um inteiro
                    # Atualizar quantidade de livros
                    update_query = f"""
                        UPDATE livros 
                        SET quantidade_copias = quantidade_copias + 1 
                        WHERE livro_id = {livro_id}
                    """
                    update_data(self.connection, update_query, None)

                self.connection.commit()  # type: ignore
                return True
            except Exception as e:
                print(f"Erro ao atualizar status: {e}")
                self.connection.rollback()  # type: ignore
                return False
        return False

    def generate_fine(self, emprestimo_id, dias_atraso):
        """Gera uma multa para empréstimo com atraso"""
        if self.ensure_connection():
            try:
                valor_multa = float("2.00") * dias_atraso
                columns = ["emprestimo_id", "valor", "status_multas", "data_geracao"]
                query = create_insert_query("multas", columns)
                values = (emprestimo_id, valor_multa, "Devendo", datetime.now().date())
                insert_data(self.connection, query, values)
                self.connection.commit()  # type: ignore
                return valor_multa
            except Exception as e:
                print(f"Erro ao gerar multa: {e}")
                self.connection.rollback()  # type: ignore
                return None
        return None

    def load_active_loans(self):
        """Carrega e exibe os empréstimos ativos"""
        try:
            # Limpar dados existentes
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)

            # Carregar empréstimos ativos
            usuario_id = self.user_id_entry.get()
            if not usuario_id:
                messagebox.showwarning("Aviso", "Digite o ID do usuário")
                return

            loans = self.fetch_active_loans(usuario_id)
            for loan in loans:  # type: ignore
                self.loans_tree.insert("", "end", values=loan)  # type: ignore

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar empréstimos: {str(e)}")

    def return_interface(self):
        """Interface principal para devolução de livros"""
        try:
            self.clear_right_frames()

            # Frame principal da devolução
            return_frame = tk.LabelFrame(
                self.main_frame, text="Devolução de Livros", padx=10, pady=5
            )
            return_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para entrada do ID do usuário
            user_frame = ttk.Frame(return_frame)
            user_frame.grid(row=0, column=0, pady=5)

            ttk.Label(user_frame, text="ID do Usuário:").grid(row=0, column=0, padx=5)
            self.user_id_entry = ttk.Entry(user_frame)
            self.user_id_entry.grid(row=0, column=1, padx=5)

            ttk.Button(
                user_frame, text="Buscar Empréstimos", command=self.load_active_loans
            ).grid(row=0, column=2, padx=5)

            # Treeview para lista de empréstimos
            self.loans_tree = ttk.Treeview(
                return_frame,
                columns=(
                    "ID",
                    "Livro ID",
                    "Título",
                    "Data Empréstimo",
                    "Data Prevista",
                ),
                show="headings",
            )

            # Configurar colunas
            self.loans_tree.heading("ID", text="ID")
            self.loans_tree.heading("Livro ID", text="Livro ID")
            self.loans_tree.heading("Título", text="Título")
            self.loans_tree.heading("Data Empréstimo", text="Data Empréstimo")
            self.loans_tree.heading("Data Prevista", text="Data Prevista")

            self.loans_tree.column("ID", width=50)
            self.loans_tree.column("Livro ID", width=70)
            self.loans_tree.column("Título", width=200)
            self.loans_tree.column("Data Empréstimo", width=100)
            self.loans_tree.column("Data Prevista", width=100)

            self.loans_tree.grid(row=1, column=0, pady=10, sticky="nsew")

            # Scrollbar
            scrollbar = ttk.Scrollbar(
                return_frame, orient="vertical", command=self.loans_tree.yview
            )
            scrollbar.grid(row=1, column=1, sticky="ns")
            self.loans_tree.configure(yscrollcommand=scrollbar.set)

            # Botão de devolução
            ttk.Button(
                return_frame, text="Confirmar Devolução", command=self.process_return_from_interface  # type: ignore
            ).grid(row=2, column=0, pady=10)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def process_return_from_interface(self):
        """Processa a devolução dos livros selecionados na interface de retorno"""
        try:
            selected_items = self.loans_tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    "Aviso", "Selecione pelo menos um livro para devolução"
                )
                return

            success_count = 0
            multas_geradas = []

            for item in selected_items:
                emprestimo_id = self.loans_tree.item(item)["values"][0]
                data_prevista = datetime.strptime(
                    self.loans_tree.item(item)["values"][4], "%Y-%m-%d"
                ).date()

                # Calcular atraso
                dias_atraso = (datetime.now().date() - data_prevista).days

                # Processar devolução
                if self.process_return(emprestimo_id):
                    success_count += 1
                    # Gerar multa se houver atraso
                    if dias_atraso > 0:
                        valor_multa = self.generate_fine(emprestimo_id, dias_atraso)
                        if valor_multa:
                            multas_geradas.append((emprestimo_id, valor_multa))

            # Feedback ao usuário
            if success_count > 0:
                if multas_geradas:
                    multas_msg = "\n".join(
                        [
                            f"Empréstimo {emp_id}: R$ {valor:.2f}"
                            for emp_id, valor in multas_geradas
                        ]
                    )
                    messagebox.showinfo(
                        "Devolução Realizada",
                        f"Devolução processada com sucesso!\n\n"
                        f"Multas geradas:\n{multas_msg}",
                    )
                else:
                    messagebox.showinfo(
                        "Devolução Realizada",
                        "Devolução processada com sucesso!\nNenhuma multa gerada.",
                    )
                self.load_active_loans()  # Atualiza a lista
            else:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhuma devolução foi processada. Verifique os itens selecionados.",
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar devolução: {str(e)}")

    def fetch_user_fines(self, usuario_id):
        """Recupera todas as multas de um usuário específico"""
        if self.ensure_connection():
            query = f"""
                SELECT m.multa_id, m.emprestimo_id, m.valor, 
                       m.status_multas, m.data_geracao, m.data_pagamento
                FROM multas m
                JOIN emprestimos e ON m.emprestimo_id = e.emprestimo_id
                WHERE e.usuario_id = {usuario_id}
                ORDER BY m.data_geracao DESC
            """
            return read_data(self.connection, query)
        return []

    def update_fine_status(self, multa_id):
        """Atualiza o status da multa para Quitado"""
        if self.ensure_connection():
            try:
                multa_id = int(multa_id)
                current_date = datetime.now().date()

                update_query = f"""
                    UPDATE multas 
                    SET status_multas = 'Quitado',
                        data_pagamento = '{current_date}'
                    WHERE multa_id = {multa_id}
                    AND status_multas = 'Devendo'
                """
                update_data(self.connection, update_query, None)
                self.connection.commit()  # type: ignore
                return True
            except Exception as e:
                print(f"Erro ao atualizar multa: {e}")
                self.connection.rollback()  # type: ignore
                return False
        return False

    def process_payment(self):
        """Processa o pagamento das multas selecionadas"""
        try:
            selected_items = self.fines_tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    "Aviso", "Selecione pelo menos uma multa para quitar"
                )
                return

            success_count = 0
            for item in selected_items:
                multa_id = self.fines_tree.item(item)["values"][0]
                status = self.fines_tree.item(item)["values"][3]

                if status == "Devendo":
                    if self.update_fine_status(multa_id):
                        success_count += 1

            if success_count > 0:
                messagebox.showinfo(
                    "Sucesso", f"{success_count} multa(s) quitada(s) com sucesso!"
                )
                self.load_user_fines()  # Atualiza a lista
            else:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhuma multa foi atualizada. Verifique se as multas selecionadas já estão quitadas.",
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar pagamento: {str(e)}")

    def load_user_fines(self):
        """Carrega e exibe as multas do usuário"""
        try:
            # Limpar dados existentes
            for item in self.fines_tree.get_children():
                self.fines_tree.delete(item)

            # Carregar multas
            usuario_id = self.user_id_entry.get()
            if not usuario_id:
                messagebox.showwarning("Aviso", "Digite o ID do usuário")
                return

            fines = self.fetch_user_fines(usuario_id)
            for fine in fines:  # type: ignore
                # Formatar valores para exibição
                formatted_fine = list(fine)
                formatted_fine[2] = f"R$ {float(fine[2]):.2f}"  # type: ignore  # type: ignore # Formatar valor
                formatted_fine[4] = fine[4].strftime("%Y-%m-%d")  # type: ignore # Formatar data geração
                if fine[5]:  # type: ignore # Data pagamento
                    formatted_fine[5] = fine[5].strftime("%Y-%m-%d")  # type: ignore
                self.fines_tree.insert("", "end", values=formatted_fine)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar multas: {str(e)}")

    def fine_interface(self):
        """Interface principal para gerenciamento de multas"""
        try:
            self.clear_right_frames()

            # Frame principal das multas
            fine_frame = tk.LabelFrame(
                self.main_frame, text="Gerenciamento de Multas", padx=10, pady=5
            )
            fine_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para entrada do ID do usuário
            user_frame = ttk.Frame(fine_frame)
            user_frame.grid(row=0, column=0, pady=5)

            ttk.Label(user_frame, text="ID do Usuário:").grid(row=0, column=0, padx=5)
            self.user_id_entry = ttk.Entry(user_frame)
            self.user_id_entry.grid(row=0, column=1, padx=5)

            ttk.Button(
                user_frame, text="Buscar Multas", command=self.load_user_fines
            ).grid(row=0, column=2, padx=5)

            # Treeview para lista de multas
            self.fines_tree = ttk.Treeview(
                fine_frame,
                columns=(
                    "ID",
                    "Empréstimo ID",
                    "Valor",
                    "Status",
                    "Data Geração",
                    "Data Pagamento",
                ),
                show="headings",
            )

            # Configurar colunas
            self.fines_tree.heading("ID", text="ID")
            self.fines_tree.heading("Empréstimo ID", text="Empréstimo ID")
            self.fines_tree.heading("Valor", text="Valor")
            self.fines_tree.heading("Status", text="Status")
            self.fines_tree.heading("Data Geração", text="Data Geração")
            self.fines_tree.heading("Data Pagamento", text="Data Pagamento")

            # Ajustar largura das colunas
            self.fines_tree.column("ID", width=50)
            self.fines_tree.column("Empréstimo ID", width=100)
            self.fines_tree.column("Valor", width=100)
            self.fines_tree.column("Status", width=100)
            self.fines_tree.column("Data Geração", width=100)
            self.fines_tree.column("Data Pagamento", width=100)

            self.fines_tree.grid(row=1, column=0, pady=10, sticky="nsew")

            # Scrollbar
            scrollbar = ttk.Scrollbar(
                fine_frame, orient="vertical", command=self.fines_tree.yview
            )
            scrollbar.grid(row=1, column=1, sticky="ns")
            self.fines_tree.configure(yscrollcommand=scrollbar.set)

            # Botão para quitar multas
            ttk.Button(
                fine_frame, text="Marcar como Quitado", command=self.process_payment
            ).grid(row=2, column=0, pady=10)

            # Configurar expansão do grid
            fine_frame.grid_columnconfigure(0, weight=1)
            fine_frame.grid_rowconfigure(1, weight=1)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def fetch_user_borrows(self, usuario_id):
        """Recupera todos os empréstimos de um usuário específico"""
        if self.ensure_connection():
            query = f"""
                SELECT e.emprestimo_id, e.livro_id, l.titulo, 
                       e.data_emprestimo, e.data_devolucao_prevista,
                       e.data_devolucao_real, e.status_emprestimo
                FROM emprestimos e
                JOIN livros l ON e.livro_id = l.livro_id
                WHERE e.usuario_id = {usuario_id}
                ORDER BY e.data_emprestimo DESC
            """
            return read_data(self.connection, query)
        return []

    def process_return(self, emprestimo_id):
        """Processa a devolução de um empréstimo e gera multa se necessário"""
        if self.ensure_connection():
            try:
                emprestimo_id = int(emprestimo_id)
                current_date = datetime.now().date()

                # Buscar informações do empréstimo
                query = f"""
                    SELECT data_devolucao_prevista, livro_id 
                    FROM emprestimos 
                    WHERE emprestimo_id = {emprestimo_id}
                """
                result = read_data(self.connection, query)

                if not result:
                    return False

                data_prevista = result[0][0]  # type: ignore
                livro_id = result[0][1]  # type: ignore

                # Calcular atraso
                dias_atraso = (current_date - data_prevista).days # type: ignore

                # Atualizar status do empréstimo
                update_query = f"""
                    UPDATE emprestimos 
                    SET status_emprestimo = 'Devolvido',
                        data_devolucao_real = '{current_date}'
                    WHERE emprestimo_id = {emprestimo_id}
                    AND status_emprestimo = 'Ativo'
                """
                update_data(self.connection, update_query, None)

                # Atualizar quantidade de livros disponíveis
                update_query = f"""
                    UPDATE livros 
                    SET quantidade_copias = quantidade_copias + 1 
                    WHERE livro_id = {livro_id}
                """
                update_data(self.connection, update_query, None)

                # Gerar multa se houver atraso
                multa_valor = None
                if dias_atraso > 0:
                    multa_valor = self.generate_fine(emprestimo_id, dias_atraso)

                self.connection.commit()  # type: ignore
                return multa_valor if dias_atraso > 0 else True

            except Exception as e:
                print(f"Erro ao processar devolução: {e}")
                self.connection.rollback()  # type: ignore
                return False
            return False

    def process_selected_returns(self):
        """Processa a devolução dos empréstimos selecionados"""
        try:
            selected_items = self.borrows_tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    "Aviso", "Selecione pelo menos um empréstimo para retorno"
                )
                return

            multas_geradas = []
            success_count = 0

            for item in selected_items:
                emprestimo_id = self.borrows_tree.item(item)["values"][0]
                status = self.borrows_tree.item(item)["values"][6]

                if status == "Ativo":
                    result = self.process_return(emprestimo_id)
                    if result:
                        success_count += 1
                        if isinstance(result, float):  # Se retornou valor de multa
                            multas_geradas.append((emprestimo_id, result))

            # Feedback ao usuário
            if success_count > 0:
                if multas_geradas:
                    multas_msg = "\n".join(
                        [
                            f"Empréstimo {emp_id}: R$ {valor:.2f}"
                            for emp_id, valor in multas_geradas
                        ]
                    )
                    messagebox.showinfo(
                        "Devolução Realizada",
                        f"{success_count} empréstimo(s) processado(s) com sucesso!\n\n"
                        f"Multas geradas:\n{multas_msg}",
                    )
                else:
                    messagebox.showinfo(
                        "Devolução Realizada",
                        f"{success_count} empréstimo(s) processado(s) com sucesso!\n"
                        "Nenhuma multa gerada.",
                    )
                self.load_user_borrows()  # Atualiza a lista
            else:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum empréstimo foi processado. Verifique se os empréstimos selecionados estão ativos.",
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar retornos: {str(e)}")

    def load_user_borrows(self):
        """Carrega e exibe os empréstimos do usuário"""
        try:
            # Limpar dados existentes
            for item in self.borrows_tree.get_children():
                self.borrows_tree.delete(item)

            # Carregar empréstimos
            usuario_id = self.user_id_entry.get()
            if not usuario_id:
                messagebox.showwarning("Aviso", "Digite o ID do usuário")
                return

            borrows = self.fetch_user_borrows(usuario_id)
            for borrow in borrows:  # type: ignore
                # Formatar valores para exibição
                formatted_borrow = list(borrow)
                formatted_borrow[3] = borrow[3].strftime(  # type: ignore
                    "%Y-%m-%d"
                )  # data_emprestimo # type: ignore
                formatted_borrow[4] = borrow[4].strftime(  # type: ignore
                    "%Y-%m-%d"
                )  # data_devolucao_prevista # type: ignore
                if borrow[5]:  # data_devolucao_real # type: ignore
                    formatted_borrow[5] = borrow[5].strftime("%Y-%m-%d")  # type: ignore
                self.borrows_tree.insert("", "end", values=formatted_borrow)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar empréstimos: {str(e)}")

    def print_borrow_interface(self):
        """Interface principal para visualização e gerenciamento de empréstimos"""
        try:
            self.clear_right_frames()

            # Frame principal dos empréstimos
            borrow_frame = tk.LabelFrame(
                self.main_frame, text="Visualização de Empréstimos", padx=10, pady=5
            )
            borrow_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para entrada do ID do usuário
            user_frame = ttk.Frame(borrow_frame)
            user_frame.grid(row=0, column=0, pady=5)

            ttk.Label(user_frame, text="ID do Usuário:").grid(row=0, column=0, padx=5)
            self.user_id_entry = ttk.Entry(user_frame)
            self.user_id_entry.grid(row=0, column=1, padx=5)

            ttk.Button(
                user_frame, text="Buscar Empréstimos", command=self.load_user_borrows
            ).grid(row=0, column=2, padx=5)

            # Treeview para lista de empréstimos
            self.borrows_tree = ttk.Treeview(
                borrow_frame,
                columns=(
                    "ID",
                    "Livro ID",
                    "Título",
                    "Data Empréstimo",
                    "Data Prevista",
                    "Data Real",
                    "Status",
                ),
                show="headings",
            )

            # Configurar colunas
            self.borrows_tree.heading("ID", text="ID")
            self.borrows_tree.heading("Livro ID", text="Livro ID")
            self.borrows_tree.heading("Título", text="Título")
            self.borrows_tree.heading("Data Empréstimo", text="Data Empréstimo")
            self.borrows_tree.heading("Data Prevista", text="Data Prevista")
            self.borrows_tree.heading("Data Real", text="Data Real")
            self.borrows_tree.heading("Status", text="Status")

            # Ajustar largura das colunas
            self.borrows_tree.column("ID", width=50)
            self.borrows_tree.column("Livro ID", width=70)
            self.borrows_tree.column("Título", width=200)
            self.borrows_tree.column("Data Empréstimo", width=100)
            self.borrows_tree.column("Data Prevista", width=100)
            self.borrows_tree.column("Data Real", width=100)
            self.borrows_tree.column("Status", width=100)

            self.borrows_tree.grid(row=1, column=0, pady=10, sticky="nsew")

            # Scrollbar
            scrollbar = ttk.Scrollbar(
                borrow_frame, orient="vertical", command=self.borrows_tree.yview
            )
            scrollbar.grid(row=1, column=1, sticky="ns")
            self.borrows_tree.configure(yscrollcommand=scrollbar.set)

            # Botão para registrar retorno
            ttk.Button(
                borrow_frame,
                text="Registrar Retorno",
                command=self.process_selected_returns,
            ).grid(row=2, column=0, pady=10)

            # Configurar expansão do grid
            borrow_frame.grid_columnconfigure(0, weight=1)
            borrow_frame.grid_rowconfigure(1, weight=1)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def fetch_books_for_reserve(self):
        """Recupera livros com quantidade zero no inventário"""
        if self.ensure_connection():
            query = """
            SELECT l.livro_id, l.titulo, l.quantidade_copias,
                COALESCE(r.total_reservas, 0) as reservas_ativas
            FROM livros l
            LEFT JOIN (
                SELECT livro_id, COUNT(*) as total_reservas
                FROM reservas
                WHERE status_reservas = 'Pendente'
                GROUP BY livro_id
            ) r ON l.livro_id = r.livro_id
            WHERE l.quantidade_copias = 0
            ORDER BY l.titulo
            """
            return read_data(self.connection, query)
        return []

    def check_existing_reserve(self, livro_id, usuario_id):
        """Verifica se o usuário já tem uma reserva ativa para o livro"""
        if self.ensure_connection():
            query = f"""
            SELECT COUNT(*) 
            FROM reservas 
            WHERE livro_id = {livro_id} 
            AND usuario_id = {usuario_id}
            AND status_reservas = 'Pendente'
            """
            result = read_data(self.connection, query)
            return result[0][0] > 0 if result else False # type: ignore
        return False

    def create_reserve(self, livro_id, usuario_id):
        """Cria uma nova reserva no banco de dados"""
        if self.ensure_connection():
            try:
                current_date = datetime.now().date()

                # Verificar se já existe reserva
                if self.check_existing_reserve(livro_id, usuario_id):
                    return False, "Você já possui uma reserva ativa para este livro"

                # Inserir reserva
                columns = ["livro_id", "usuario_id", "data_reserva", "status_reservas"]
                query = create_insert_query("reservas", columns)
                values = (livro_id, usuario_id, current_date, "Pendente")

                insert_data(self.connection, query, values)
                self.connection.commit() # type: ignore
                return True, "Reserva realizada com sucesso!"

            except Exception as e:
                self.connection.rollback() # type: ignore
                return False, f"Erro ao criar reserva: {str(e)}"
        return False, "Erro de conexão com o banco de dados"

    def reserve_interface(self):
        """Interface principal para reserva de livros"""
        try:
            self.clear_right_frames()

            # Frame principal da reserva
            reserve_frame = tk.LabelFrame(
                self.main_frame, text="Reserva de Livros", padx=10, pady=5
            )
            reserve_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para entrada do ID do usuário
            user_frame = ttk.Frame(reserve_frame)
            user_frame.grid(row=0, column=0, pady=5)

            ttk.Label(user_frame, text="ID do Usuário:").grid(row=0, column=0, padx=5)
            self.user_id_entry = ttk.Entry(user_frame)
            self.user_id_entry.grid(row=0, column=1, padx=5)

            # Treeview para lista de livros
            self.reserve_tree = ttk.Treeview(
                reserve_frame,
                columns=(
                    "ID",
                    "Título",
                    "Qtd Disponível",
                    "Reservas Ativas"
                ),
                show="headings",
            )

            # Configurar colunas
            self.reserve_tree.heading("ID", text="ID")
            self.reserve_tree.heading("Título", text="Título")
            self.reserve_tree.heading("Qtd Disponível", text="Qtd Disponível")
            self.reserve_tree.heading("Reservas Ativas", text="Reservas Ativas")

            # Ajustar largura das colunas
            self.reserve_tree.column("ID", width=50)
            self.reserve_tree.column("Título", width=300)
            self.reserve_tree.column("Qtd Disponível", width=100)
            self.reserve_tree.column("Reservas Ativas", width=100)

            self.reserve_tree.grid(row=1, column=0, pady=10, sticky="nsew")

            # Scrollbar
            scrollbar = ttk.Scrollbar(
                reserve_frame, orient="vertical", command=self.reserve_tree.yview
            )
            scrollbar.grid(row=1, column=1, sticky="ns")
            self.reserve_tree.configure(yscrollcommand=scrollbar.set)

            # Frame para botões
            button_frame = ttk.Frame(reserve_frame)
            button_frame.grid(row=2, column=0, pady=10)

            # Botão para atualizar lista
            ttk.Button(
                button_frame,
                text="Atualizar Lista",
                command=self.load_books_for_reserve
            ).grid(row=0, column=0, padx=5)

            # Botão para realizar reserva
            ttk.Button(
                button_frame,
                text="Realizar Reserva",
                command=self.process_reserve
            ).grid(row=0, column=1, padx=5)

            # Carregar livros inicialmente
            self.load_books_for_reserve()

            # Configurar expansão do grid
            reserve_frame.grid_columnconfigure(0, weight=1)
            reserve_frame.grid_rowconfigure(1, weight=1)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def load_books_for_reserve(self):
        """Carrega e exibe os livros disponíveis para reserva"""
        try:
            # Limpar dados existentes
            for item in self.reserve_tree.get_children():
                self.reserve_tree.delete(item)

            # Carregar livros
            books = self.fetch_books_for_reserve()
            for book in books: # type: ignore
                self.reserve_tree.insert("", "end", values=book) # type: ignore

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar livros: {str(e)}")


    def process_reserve(self):
        """Processa a reserva dos livros selecionados"""
        try:
            # Verificar se um usuário foi informado
            usuario_id = self.user_id_entry.get()
            if not usuario_id:
                messagebox.showwarning("Aviso", "Digite o ID do usuário")
                return

            # Verificar se um livro foi selecionado
            selected_items = self.reserve_tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    "Aviso", "Selecione um livro para reserva"
                )
                return

            # Processar cada livro selecionado
            success_count = 0
            for item in selected_items:
                livro_id = self.reserve_tree.item(item)["values"][0]

                # Criar reserva
                if self.create_reserve(livro_id, usuario_id):
                    success_count += 1

            if success_count > 0:
                messagebox.showinfo(
                    "Sucesso", 
                    f"{success_count} reserva(s) realizada(s) com sucesso!"
                )
                self.load_books_for_reserve()  # Atualizar lista
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhuma reserva foi processada. Verifique se você já possui reservas para estes livros."
                )

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar reserva: {str(e)}")


