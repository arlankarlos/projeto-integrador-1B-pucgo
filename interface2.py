import tkinter as tk
from tkinter import messagebox, ttk
from db_utils import get_database_connection, create_update_query, update_data
from read_update_delete_user import delete_user, print_user, read_user
from create_user import create_user
from validate_utils import validate_email, validate_phone, validate_cep, validate_uf
import datetime


class UserManagementInterface:
    def __init__(self, connection=None):
        self.connection = connection
        self.root = tk.Tk()
        self.root.title("Gerenciamento de Usuários")
        self.root.geometry("800x600")  # Aumentando a largura para acomodar a disposição
        self.user_frame = None
        self.address_frame = None

        # Configurando estilo
        self.configure_style()

        # Criando frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")

        # Criando os botões inicialmente
        self.create_buttons()


    def ensure_connection(self):
        """
        Verifica se a conexão está ativa e tenta reconectar se necessário
        """
        if not self.connection or not self.connection.is_connected():
            self.connection = get_database_connection()
            if not self.connection:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
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

    def create_user_fields(self):
        """Cria os campos de dados do usuário"""
        self.user_frame = tk.LabelFrame(
            self.main_frame, text="Dados do Usuário", padx=10, pady=5
        )
        self.user_frame.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=5
        )  # Colocando à direita

        # Campo ID
        tk.Label(self.user_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        self.id_entry = tk.Entry(self.user_frame)
        self.id_entry.grid(row=0, column=1, sticky="w", pady=2)

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
        """Cria os botões da interface"""
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.grid(
            row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=5
        )  # Colocando à esquerda

        buttons = [
            ("Criar Usuário", self.create_user_interface),
            ("Atualizar Usuário", self.update_user_interface),
            ("Deletar Usuário", self.delete_user_interface),
            ("Buscar Usuário", self.print_user_interface),
        ]

        for text, command in buttons:
            btn = tk.Button(
                buttons_frame, text=text, command=command, **self.button_style
            )
            btn.pack(pady=5)

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
            # connection = get_database_connection()
            
            if self.connection:
                create_user(self.connection)
                self.connection.close()
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                self.clear_right_frames()  # Limpa os campos após salvar
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {str(e)}")

    def clear_right_frames(self):
        """Limpa todos os widgets na coluna direita"""
        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["column"]) == 1:
                widget.destroy()

    def update_user_interface(self):
        """Interface para atualizar usuário"""
        self.clear_right_frames()

        # Criar frame de busca para atualização
        search_frame = tk.LabelFrame(self.main_frame, text="Buscar Usuário para Atualização", padx=10, pady=5)
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
            command=lambda: self.perform_update(id_entry.get().strip(), email_entry.get().strip()),
            **self.button_style
        )
        search_button.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_user_interface(self):
        """Interface para deletar usuário"""
        self.clear_right_frames()

        # Criar frame de busca para deleção
        delete_frame = tk.LabelFrame(self.main_frame, text="Deletar Usuário", padx=10, pady=5)
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
            command=lambda: self.perform_delete(id_entry.get().strip(), email_entry.get().strip()),
            **self.button_style
        )
        delete_button.grid(row=2, column=0, columnspan=2, pady=10)

    # def perform_update(self, usuario_id, email):
    #     """
    #     Executa a atualização do usuário
    #     """
    #     connection = get_database_connection()
    #     if not connection:
    #         print(f"[{datetime.datetime.now()}] Erro: Conexão com o banco de dados não disponível.")
    #         messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
    #         return False
        
    #     if not usuario_id and not email:
    #         messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
    #         return False

    #     try:

    #         # Busca o usuário e mostra os dados atuais
    #         result = read_user(
    #             connection,
    #             usuario_id=usuario_id if usuario_id else None,
    #             email=email if email else None,
    #         )

    #         if not result:
    #             messagebox.showinfo("Aviso", "Usuário não encontrado!")
    #             return False

    #         # Limpa a área direita e cria os campos de atualização
    #         self.clear_right_frames()

    #         # Cria frame para atualização
    #         update_frame = tk.LabelFrame(
    #             self.main_frame, text="Atualizar Usuário", padx=10, pady=5
    #         )
    #         update_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

    #         # Preenche os campos com os dados atuais
    #         row = result[0]

    #         # Campos de usuário
    #         fields = [
    #             ("Nome", row[1]),
    #             ("Email", row[2]),
    #             ("Telefone", row[3]),
    #             ("Status", row[5]),
    #         ]

    #         entries = {}
    #         for i, (label, value) in enumerate(fields):
    #             tk.Label(update_frame, text=f"{label}:").grid(
    #                 row=i, column=0, sticky="e", pady=2
    #             )
    #             entry = tk.Entry(update_frame)
    #             entry.insert(0, value)
    #             entry.grid(row=i, column=1, sticky="w", pady=2)
    #             entries[label.lower()] = entry

    #         def save_updates():
    #             updates = {}
    #             if entries["nome"].get().strip() != row[1]:
    #                 updates["nome"] = entries["nome"].get().strip()
    #             if entries["email"].get().strip() != row[2]:
    #                 updates["email"] = entries["email"].get().strip()
    #             if entries["telefone"].get().strip() != row[3]:
    #                 updates["telefone"] = entries["telefone"].get().strip()
    #             if entries["status"].get().strip() != row[5]:
    #                 updates["status_usuario"] = entries["status"].get().strip()

    #             if not updates:
    #                 messagebox.showinfo("Aviso", "Nenhuma alteração detectada!")
    #                 return

    #             try:
    #                 condition = f"usuario_id = {row[0]}"
    #                 query = create_update_query("usuarios", updates.keys(), condition)
    #                 update_data(connection, query, tuple(updates.values()))

    #                 messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
    #                 self.clear_right_frames()

    #                 # Log da atualização
    #                 print(
    #                     f"[{datetime.datetime.now()}] Usuário {row[0]} atualizado. Campos alterados: {', '.join(updates.keys())}"
    #                 )

    #             except Exception as e:
    #                 messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
    #                 print(
    #                     f"[{datetime.datetime.now()}] Erro ao atualizar usuário {row[0]}: {str(e)}"
    #                 )

    #         # Botões de ação
    #         buttons_frame = tk.Frame(update_frame)
    #         buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

    #         save_button = tk.Button(
    #             buttons_frame,
    #             text="Salvar Alterações",
    #             command=save_updates,
    #             **self.button_style,
    #         )
    #         save_button.pack(side=tk.LEFT, padx=5)

    #         cancel_button = tk.Button(
    #             buttons_frame,
    #             text="Cancelar",
    #             command=self.clear_right_frames,
    #             **self.button_style,
    #         )
    #         cancel_button.pack(side=tk.LEFT, padx=5)

    #     except Exception as e:
    #         print(f"[{datetime.datetime.now()}] Erro ao atualizar usuário {usuario_id}: {str(e)}")
    #     finally:
    #         if connection.is_connected():
    #             connection.close()
    #             print(f"[{datetime.datetime.now()}] Conexão com o banco de dados encerrada.")

    def perform_update(self, usuario_id, email):
        """
        Executa a atualização do usuário
        """
        if not self.connection or not self.connection.is_connected():
            print(f"[{datetime.datetime.now()}] Erro: Conexão com o banco de dados não disponível.")
            self.connection = get_database_connection()  # Tenta reconectar
            if not self.connection:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
                return False

        try:
            # Busca o usuário
            result = read_user(self.connection, 
                            usuario_id=usuario_id if usuario_id else None,
                            email=email if email else None)

            if not result:
                messagebox.showinfo("Aviso", "Usuário não encontrado!")
                return False

            # Limpa a área direita e cria os campos de atualização
            self.clear_right_frames()

            # Cria frame para atualização
            update_frame = tk.LabelFrame(self.main_frame, text="Atualizar Usuário", padx=10, pady=5)
            update_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Preenche os campos com os dados atuais
            row = result[0]

            # Campos de usuário com seus valores atuais
            fields = [
                ("Nome", row[1]),
                ("Email", row[2]),
                ("Telefone", row[3]),
                ("Status", row[5])
            ]

            entries = {}
            for i, (label, value) in enumerate(fields):
                tk.Label(update_frame, text=f"{label}:").grid(row=i, column=0, sticky="e", pady=2)
                entry = tk.Entry(update_frame)
                entry.insert(0, value)
                entry.grid(row=i, column=1, sticky="w", pady=2)
                entries[label.lower()] = entry

            def save_updates():
                # Verifica se a conexão ainda está ativa
                if not self.connection or not self.connection.is_connected():
                    self.connection = get_database_connection()
                    if not self.connection:
                        messagebox.showerror("Erro", "Conexão com o banco de dados perdida!")
                        return

                # Coleta as atualizações dos campos
                updates = {}
                if entries['nome'].get().strip() != row[1]:
                    updates['nome'] = entries['nome'].get().strip()
                if entries['email'].get().strip() != row[2]:
                    updates['email'] = entries['email'].get().strip()
                if entries['telefone'].get().strip() != row[3]:
                    updates['telefone'] = entries['telefone'].get().strip()
                if entries['status'].get().strip() != row[5]:
                    updates['status_usuario'] = entries['status'].get().strip()

                if not updates:
                    messagebox.showinfo("Aviso", "Nenhuma alteração detectada!")
                    return

                try:
                    # Criar e executar a query de atualização
                    condition = f"usuario_id = {row[0]}"
                    query = create_update_query("usuarios", updates.keys(), condition)
                    update_data(self.connection, query, tuple(updates.values()))

                    messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                    self.clear_right_frames()

                    # Log da atualização
                    print(f"[{datetime.datetime.now()}] Usuário {row[0]} atualizado. Campos alterados: {', '.join(updates.keys())}")

                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
                    print(f"[{datetime.datetime.now()}] Erro ao atualizar usuário {row[0]}: {str(e)}")

            # Botões de ação
            buttons_frame = tk.Frame(update_frame)
            buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

            save_button = tk.Button(
                buttons_frame,
                text="Salvar Alterações",
                command=save_updates,
                **self.button_style
            )
            save_button.pack(side=tk.LEFT, padx=5)

            cancel_button = tk.Button(
                buttons_frame,
                text="Cancelar",
                command=self.clear_right_frames,
                **self.button_style
            )
            cancel_button.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preparar atualização: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao preparar atualização: {str(e)}")
            return False

    def perform_delete(self, usuario_id, email):
        """
        Executa a exclusão do usuário
        """
        if not usuario_id and not email:
            messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
            return False

        try:
            # connection = get_database_connection()
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
            message = f"""
            Confirma a exclusão do usuário?

            ID: {row[0]}
            Nome: {row[1]}
            Email: {row[2]}
            Telefone: ({row[3][:2]}) {row[3][2:7]}-{row[3][7:]}
            Status: {row[5]}
            """

            if not messagebox.askyesno("Confirmar Exclusão", message):
                return False

            # Executa a exclusão
            success = delete_user(self.connection, usuario_id=row[0])

            if success:
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
                self.clear_right_frames()

                # Log da exclusão
                print(
                    f"[{datetime.datetime.now()}] Usuário {row[0]} ({row[1]}) excluído com sucesso."
                )
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o usuário.")
                print(
                    f"[{datetime.datetime.now()}] Falha ao excluir usuário {row[0]} ({row[1]})."
                )

            return success

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
            print(f"[{datetime.datetime.now()}] Erro ao excluir usuário: {str(e)}")
            return False
        finally:
            if self.connection:
                self.connection.close()

    def print_user_interface(self):
        """Interface para buscar usuário"""
        # Limpa os campos existentes
        self.clear_fields()

        # Esconde os frames existentes
        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["column"]) == 1:  # Widgets na coluna direita
                widget.grid_remove()

        # Cria frame de busca
        search_frame = tk.LabelFrame(
            self.main_frame, text="Buscar Usuário", padx=10, pady=5
        )
        search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campo ID
        tk.Label(search_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        id_entry = tk.Entry(search_frame)
        id_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Campo Email
        tk.Label(search_frame, text="Email:").grid(row=1, column=0, sticky="e", pady=2)
        email_entry = tk.Entry(search_frame)
        email_entry.grid(row=1, column=1, sticky="w", pady=2)

        def search():
            usuario_id = id_entry.get().strip()
            email = email_entry.get().strip()

            if not usuario_id and not email:
                messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
                return

            try:
                # connection = get_database_connection()
                if self.connection:
                    result = print_user(
                        self.connection,
                        usuario_id=usuario_id if usuario_id else None,
                        email=email if email else None,
                    )
                    self.connection.close()

                    if not result:
                        messagebox.showinfo("Aviso", "Usuário não encontrado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar usuário: {str(e)}")

        # Botão de busca
        search_button = tk.Button(
            search_frame, text="Buscar", command=search, **self.button_style
        )
        search_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Área para exibir resultados
        result_frame = tk.LabelFrame(
            self.main_frame, text="Resultado da Busca", padx=10, pady=5
        )
        result_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        # Configurar um widget Text para mostrar os resultados
        self.result_text = tk.Text(result_frame, height=10, width=40)
        self.result_text.pack(padx=5, pady=5)

        # Modificar a função print_user para mostrar os resultados na interface
        def custom_print(*args):
            self.result_text.insert(tk.END, " ".join(map(str, args)) + "\n")

        # Sobrescrever temporariamente a função print
        import builtins

        original_print = builtins.print
        builtins.print = custom_print

        def restore_interface():
            """Restaura a interface original"""
            # Restaura a função print original
            builtins.print = original_print

            # Remove os frames de busca
            search_frame.grid_remove()
            result_frame.grid_remove()

            # Restaura os frames originais
            self.create_user_fields()
            self.create_address_fields()

        # Botão para voltar
        back_button = tk.Button(
            search_frame, text="Voltar", command=restore_interface, **self.button_style
        )
        back_button.grid(row=3, column=0, columnspan=2, pady=10)

    def clear_fields(self):
        """Limpa todos os campos"""
        entries = [
            self.id_entry,
            self.name_entry,
            self.email_entry,
            self.phone_entry,
            self.street_entry,
            self.number_entry,
            self.complement_entry,
            self.district_entry,
            self.cep_entry,
            self.city_entry,
            self.state_entry,
        ]
        for entry in entries:
            entry.delete(0, tk.END)
        self.status_var.set("Ativo")

    def run(self):
        """Inicia o loop da interface gráfica"""
        self.root.mainloop()


def create_interface(connection=None):
    return UserManagementInterface(connection)
