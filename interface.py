import tkinter as tk
from tkinter import messagebox, ttk
from db_utils import get_database_connection
from read_update_delete_user import update_user, delete_user, print_user
from create_user import create_user
from validate_utils import validate_email, validate_phone, validate_cep, validate_uf
import datetime

class UserManagementInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerenciamento de Usuários")
        self.root.geometry("500x800")

        # Configurando estilo
        self.configure_style()

        # Criando frame principal com scroll
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')

        # Criando os campos de entrada
        self.create_user_fields()
        self.create_address_fields()
        self.create_buttons()

    def configure_style(self):
        self.root.configure(bg='#f0f0f0')
        self.button_style = {
            'font': ('Arial', 11),
            'width': 20,
            'bg': '#4CAF50',
            'fg': 'white',
            'relief': tk.RAISED,
            'cursor': 'hand2'
        }

    def create_user_fields(self):
        """Cria os campos de dados do usuário"""
        user_frame = tk.LabelFrame(self.main_frame, text="Dados do Usuário", padx=10, pady=5)
        user_frame.pack(fill="x", padx=10, pady=5)

        # Campo ID
        tk.Label(user_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        self.id_entry = tk.Entry(user_frame)
        self.id_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Campo Nome
        tk.Label(user_frame, text="Nome:").grid(row=1, column=0, sticky="e", pady=2)
        self.name_entry = tk.Entry(user_frame)
        self.name_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Campo Email
        tk.Label(user_frame, text="Email:").grid(row=2, column=0, sticky="e", pady=2)
        self.email_entry = tk.Entry(user_frame)
        self.email_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Campo Telefone
        tk.Label(user_frame, text="Telefone:").grid(row=3, column=0, sticky="e", pady=2)
        self.phone_entry = tk.Entry(user_frame)
        self.phone_entry.grid(row=3, column=1, sticky="w", pady=2)

        # Campo Status
        tk.Label(user_frame, text="Status:").grid(row=4, column=0, sticky="e", pady=2)
        self.status_var = tk.StringVar(value="Ativo")
        self.status_combo = ttk.Combobox(user_frame, textvariable=self.status_var, values=["Ativo", "Inativo"])
        self.status_combo.grid(row=4, column=1, sticky="w", pady=2)

    def create_address_fields(self):
        """Cria os campos de endereço"""
        address_frame = tk.LabelFrame(self.main_frame, text="Endereço", padx=10, pady=5)
        address_frame.pack(fill="x", padx=10, pady=5)

        # Logradouro
        tk.Label(address_frame, text="Logradouro:").grid(row=0, column=0, sticky="e", pady=2)
        self.street_entry = tk.Entry(address_frame)
        self.street_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Número
        tk.Label(address_frame, text="Número:").grid(row=1, column=0, sticky="e", pady=2)
        self.number_entry = tk.Entry(address_frame)
        self.number_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Complemento
        tk.Label(address_frame, text="Complemento:").grid(row=2, column=0, sticky="e", pady=2)
        self.complement_entry = tk.Entry(address_frame)
        self.complement_entry.grid(row=2, column=1, sticky="w", pady=2)

        # Bairro
        tk.Label(address_frame, text="Bairro:").grid(row=3, column=0, sticky="e", pady=2)
        self.district_entry = tk.Entry(address_frame)
        self.district_entry.grid(row=3, column=1, sticky="w", pady=2)

        # CEP
        tk.Label(address_frame, text="CEP:").grid(row=4, column=0, sticky="e", pady=2)
        self.cep_entry = tk.Entry(address_frame)
        self.cep_entry.grid(row=4, column=1, sticky="w", pady=2)

        # Cidade
        tk.Label(address_frame, text="Cidade:").grid(row=5, column=0, sticky="e", pady=2)
        self.city_entry = tk.Entry(address_frame)
        self.city_entry.grid(row=5, column=1, sticky="w", pady=2)

        # Estado
        tk.Label(address_frame, text="Estado (UF):").grid(row=6, column=0, sticky="e", pady=2)
        self.state_entry = tk.Entry(address_frame)
        self.state_entry.grid(row=6, column=1, sticky="w", pady=2)

    def create_buttons(self):
        """Cria os botões da interface"""
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=10)

        buttons = [
            ("Criar Usuário", self.create_user_interface),
            ("Atualizar Usuário", self.update_user_interface),
            ("Deletar Usuário", self.delete_user_interface),
            ("Buscar Usuário", self.print_user_interface)
        ]

        for text, command in buttons:
            btn = tk.Button(buttons_frame, text=text, command=command, **self.button_style)
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
            'nome': self.name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'telefone': self.phone_entry.get().strip(),
            'data_cadastro': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_address_data(self):
        """Coleta os dados de endereço dos campos"""
        return {
            'logradouro': self.street_entry.get().strip(),
            'numero': self.number_entry.get().strip() or None,
            'complemento': self.complement_entry.get().strip(),
            'bairro': self.district_entry.get().strip(),
            'cep': self.cep_entry.get().strip(),
            'cidade': self.city_entry.get().strip(),
            'estado': self.state_entry.get().strip()
        }

    def create_user_interface(self):
        """Interface para criar usuário"""
        if not self.validate_user_data() or not self.validate_address_data():
            return

        try:
            connection = get_database_connection()
            if connection:
                create_user(connection)
                connection.close()
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                self.clear_fields()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {str(e)}")

    def update_user_interface(self):
        """Interface para atualizar usuário"""
        usuario_id = self.id_entry.get().strip()
        email = self.email_entry.get().strip()

        if not usuario_id and not email:
            messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
            return

        try:
            connection = get_database_connection()
            if connection:
                update_user(connection, usuario_id=usuario_id if usuario_id else None, 
                          email=email if email else None)
                connection.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")

    def delete_user_interface(self):
        """Interface para deletar usuário"""
        usuario_id = self.id_entry.get().strip()
        email = self.email_entry.get().strip()

        if not usuario_id and not email:
            messagebox.showerror("Erro", "Informe ID ou Email do usuário!")
            return

        try:
            connection = get_database_connection()
            if connection:
                delete_user(connection, usuario_id=usuario_id if usuario_id else None, 
                          email=email if email else None)
                connection.close()
                self.clear_fields()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar usuário: {str(e)}")



    def create_search_window(self):
        """Cria uma janela para busca de usuário"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Buscar Usuário")
        search_window.geometry("300x150")

        # Frame para os campos de busca
        search_frame = tk.LabelFrame(search_window, text="Buscar por", padx=10, pady=5)
        search_frame.pack(fill="x", padx=10, pady=5)

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
                connection = get_database_connection()
                if connection:
                    result = print_user(connection, usuario_id=usuario_id if usuario_id else None, 
                                    email=email if email else None)
                    connection.close()

                    if result:  # Se encontrou o usuário
                        search_window.destroy()  # Fecha a janela de busca
                    else:
                        messagebox.showinfo("Aviso", "Usuário não encontrado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar usuário: {str(e)}")

        # Botão de busca
        search_button = tk.Button(search_window, text="Buscar", 
                                command=search, **self.button_style)
        search_button.pack(pady=10)

    def print_user_interface(self):
        """Interface para buscar usuário"""
        self.create_search_window()



    def clear_fields(self):
        """Limpa todos os campos"""
        entries = [
            self.id_entry, self.name_entry, self.email_entry, self.phone_entry,
            self.street_entry, self.number_entry, self.complement_entry,
            self.district_entry, self.cep_entry, self.city_entry, self.state_entry
        ]
        for entry in entries:
            entry.delete(0, tk.END)
        self.status_var.set("Ativo")

    def run(self):
        """Inicia o loop da interface gráfica"""
        self.root.mainloop()

def create_interface():
    return UserManagementInterface()