import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from db_utils import (
    get_database_connection,
    update_data,
    read_data,
)
from create_user import create_insert_query, insert_data
from datetime import datetime
import csv


class CategoriesManagementInterface:
    """
    Interface para gerenciamento de categorias.
    Esta classe fornece uma interface gráfica para criar categorias.
    """

    def __init__(self, connection=None):
        self.connection = connection
        self.category_frame = None
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

    def create_category_fields(self):
        """Cria os campos de dados da categoria"""
        self.category_frame = tk.LabelFrame(
            self.main_frame, text="Dados da Categoria", padx=10, pady=5
        )
        self.category_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campo ID
        tk.Label(self.category_frame, text="ID:").grid(
            row=0, column=0, sticky="e", pady=2
        )
        self.id_entry = tk.Entry(self.category_frame)
        self.id_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Campo Nome
        tk.Label(self.category_frame, text="Nome:").grid(
            row=1, column=0, sticky="e", pady=2
        )
        self.name_entry = tk.Entry(self.category_frame)
        self.name_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Campo Descrição
        tk.Label(self.category_frame, text="Descrição:").grid(
            row=2, column=0, sticky="e", pady=2
        )
        self.description_text = tk.Text(self.category_frame, height=4, width=30)
        self.description_text.grid(row=2, column=1, sticky="w", pady=2)

    def create_category_interface(self):
        """Interface para criar categoria"""
        print("Iniciando criação da interface de categoria...")  # Debug
        print(f"create_category_interface main_frame: {self.main_frame}")  # Debug

        if not self.main_frame:
            messagebox.showerror("Erro", "Frame principal não inicializado!")
            return

        try:
            self.clear_right_frames()
            self.create_category_fields()

            # Adiciona botão de salvar
            save_frame = tk.Frame(self.main_frame)
            save_frame.grid(row=2, column=1, pady=10)

            save_button = tk.Button(
                save_frame,
                text="Salvar Categoria",
                command=self.save_category,
                **self.button_style,
            )
            save_button.pack()
            print("Interface de categoria criada com sucesso!")  # Debug

        except Exception as e:
            print(f"Erro ao criar interface: {str(e)}")  # Debug
            messagebox.showerror("Erro", f"Erro ao criar interface: {str(e)}")

    def save_category(self):
        """Salva a nova categoria"""
        try:
            if not self.ensure_connection():
                return

            # Validar campos
            id_categoria = self.id_entry.get().strip()
            nome = self.name_entry.get().strip()
            descricao = self.description_text.get("1.0", tk.END).strip()

            if not nome:
                messagebox.showwarning("Aviso", "O nome da categoria é obrigatório!")
                return

            # Criar query para inserir categoria
            category_query = create_insert_query(
                "categorias", ["categoria_id", "nome", "descricao"]
            )

            # Coletar dados da categoria dos campos
            category_values = (id_categoria, nome, descricao)

            # Inserir categoria
            insert_data(self.connection, category_query, category_values)

            messagebox.showinfo("Sucesso", "Categoria criada com sucesso!")
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar categoria: {str(e)}")
            print(f"[{datetime.now()}] Erro ao criar categoria: {str(e)}")

    def update_category_interface(self):
        """Interface para atualizar categorias"""
        self.clear_right_frames()

        # Criar frame de busca para atualização
        search_frame = tk.LabelFrame(
            self.main_frame, text="Buscar Categoria para Atualização", padx=10, pady=5
        )
        search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Variável para controlar o tipo de busca
        self.search_type = tk.StringVar(value="id")

        # Radio buttons para selecionar tipo de busca
        tk.Radiobutton(
            search_frame, text="Buscar por ID", variable=self.search_type, value="id"
        ).grid(row=0, column=0, padx=5)

        tk.Radiobutton(
            search_frame,
            text="Buscar por Nome",
            variable=self.search_type,
            value="nome",
        ).grid(row=0, column=1, padx=5)

        # Campo de busca
        tk.Label(search_frame, text="Buscar:").grid(row=1, column=0, sticky="e", pady=2)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.grid(row=1, column=1, sticky="w", pady=2)

        # Botão de busca
        search_button = tk.Button(
            search_frame,
            text="Buscar",
            command=self.search_category,
            **self.button_style,
        )
        search_button.grid(row=2, column=0, columnspan=2, pady=10)

    def search_category(self):
        """Busca a categoria pelo ID ou Nome"""
        search_term = self.search_entry.get().strip()
        search_type = self.search_type.get()

        if not search_term:
            messagebox.showwarning("Aviso", "Digite um termo para busca!")
            return

        try:
            if search_type == "id":
                if not search_term.isdigit():
                    messagebox.showwarning("Aviso", "ID deve ser um número!")
                    return
                query = f"SELECT * FROM categorias WHERE categoria_id = {search_term}"
            else:
                query = f"SELECT * FROM categorias WHERE nome LIKE '%{search_term}%'"

            result = read_data(self.connection, query)

            if not result:
                messagebox.showinfo("Aviso", "Categoria não encontrada!")
                return

            if len(result) > 1:
                self.show_multiple_results(result)
            else:
                self.show_update_form(result[0])

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na busca: {str(e)}")

    def show_multiple_results(self, results):
        """Mostra uma janela com múltiplos resultados para seleção"""
        selection_window = tk.Toplevel()
        selection_window.title("Selecione uma Categoria")
        selection_window.geometry("400x300")

        tree = ttk.Treeview(
            selection_window, columns=("ID", "Nome", "Descrição"), show="headings"
        )
        for col in ["ID", "Nome", "Descrição"]:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for row in results:
            # Usando índices numéricos em vez de chaves de dicionário
            tree.insert("", "end", values=(row[0], row[1], row[2]))

        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        def on_select():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                categoria_id = item["values"][0]
                # Buscar a categoria selecionada
                categoria = next(r for r in results if r[0] == categoria_id)
                self.show_update_form(categoria)
                selection_window.destroy()

        tk.Button(
            selection_window, text="Selecionar", command=on_select, **self.button_style
        ).pack(pady=10)

    def show_update_form(self, categoria):
        """Mostra o formulário de atualização com os dados da categoria"""
        self.clear_right_frames()

        update_frame = tk.LabelFrame(
            self.main_frame, text="Atualizar Categoria", padx=10, pady=5
        )
        update_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

        # Campo ID (readonly)
        tk.Label(update_frame, text="ID:").grid(row=0, column=0, sticky="e", pady=2)
        id_entry = tk.Entry(update_frame)
        id_entry.insert(0, str(categoria[0]))  # ID
        id_entry.config(state="readonly")
        id_entry.grid(row=0, column=1, sticky="w", pady=2)

        # Campos editáveis
        tk.Label(update_frame, text="Nome:").grid(row=1, column=0, sticky="e", pady=2)
        nome_entry = tk.Entry(update_frame)
        nome_entry.insert(0, categoria[1])  # Nome
        nome_entry.grid(row=1, column=1, sticky="w", pady=2)

        tk.Label(update_frame, text="Descrição:").grid(
            row=2, column=0, sticky="e", pady=2
        )
        descricao_text = tk.Text(update_frame, height=4, width=30)
        descricao_text.insert("1.0", categoria[2] or "")  # Descrição
        descricao_text.grid(row=2, column=1, sticky="w", pady=2)

        def perform_update():
            """Executa a atualização da categoria"""
            try:
                nome = nome_entry.get().strip()
                descricao = descricao_text.get("1.0", tk.END).strip()

                if not nome:
                    messagebox.showwarning("Aviso", "Nome é obrigatório!")
                    return

                query = """
                    UPDATE categorias 
                    SET nome = %s, descricao = %s 
                    WHERE categoria_id = %s
                """
                params = (nome, descricao, categoria[0])  # ID

                update_data(self.connection, query, params)
                messagebox.showinfo("Sucesso", "Categoria atualizada com sucesso!")
                self.clear_right_frames()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar: {str(e)}")

        # Botões
        buttons_frame = tk.Frame(update_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(
            buttons_frame,
            text="Salvar Alterações",
            command=perform_update,
            **self.button_style,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_frame,
            text="Cancelar",
            command=self.clear_right_frames,
            **self.button_style,
        ).pack(side=tk.LEFT, padx=5)

    def print_category_interface(self):
        """Interface para visualização e impressão de categorias"""
        try:
            self.clear_right_frames()

            # Frame principal para a visualização
            view_frame = tk.LabelFrame(
                self.main_frame,
                text="Visualização de Categorias",
                padx=10,
                pady=5
            )
            view_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

            # Frame para os botões de controle
            control_frame = tk.Frame(view_frame)
            control_frame.pack(fill=tk.X, padx=5, pady=5)

            # Botões de controle
            tk.Button(
                control_frame,
                text="Atualizar Lista",
                command=lambda: self.load_categories_data(tree),
                **self.button_style
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                control_frame,
                text="Exportar CSV",
                command=lambda: self.export_to_csv(tree),
                **self.button_style
            ).pack(side=tk.LEFT, padx=5)

            # Frame para a busca
            search_frame = tk.Frame(view_frame)
            search_frame.pack(fill=tk.X, padx=5, pady=5)

            tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
            search_entry = tk.Entry(search_frame, width=30)
            search_entry.pack(side=tk.LEFT, padx=5)

            def search_categories():
                search_term = search_entry.get().strip().lower()
                for item in tree.get_children():
                    tree.delete(item)

                query = f"""
                    SELECT * FROM categorias 
                    WHERE LOWER(nome) LIKE '%{search_term}%' 
                    OR LOWER(descricao) LIKE '%{search_term}%'
                """
                results = read_data(self.connection, query)
                self.populate_tree(tree, results)

            tk.Button(
                search_frame,
                text="Buscar",
                command=search_categories,
                **self.button_style
            ).pack(side=tk.LEFT, padx=5)

            # Criar Treeview
            columns = ("ID", "Nome", "Descrição")
            tree = ttk.Treeview(view_frame, columns=columns, show="headings")

            # Configurar cabeçalhos
            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, c, False))
                tree.column(col, width=150)

            # Adicionar scrollbars
            y_scrollbar = ttk.Scrollbar(view_frame, orient=tk.VERTICAL, command=tree.yview)
            x_scrollbar = ttk.Scrollbar(view_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

            # Posicionar elementos
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

            # Carregar dados iniciais
            self.load_categories_data(tree)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface de visualização: {str(e)}")

    def load_categories_data(self, tree):
        """Carrega os dados das categorias na TreeView"""
        try:
            # Limpar dados existentes
            for item in tree.get_children():
                tree.delete(item)

            # Buscar dados do banco
            query = "SELECT * FROM categorias ORDER BY categoria_id"
            results = read_data(self.connection, query)

            self.populate_tree(tree, results)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

    def populate_tree(self, tree, results):
        """Popula a TreeView com os resultados"""
        for row in results:
            tree.insert("", "end", values=(
                row[0],  # ID
                row[1],  # Nome
                row[2]   # Descrição
            ))

    def sort_treeview(self, tree, col, reverse):
        """Ordena a TreeView ao clicar no cabeçalho"""
        items = [(tree.set(item, col), item) for item in tree.get_children("")]

        # Converter IDs para números quando ordenar pela coluna ID
        if col == "ID":
            items = [(int(value), item) for value, item in items]

        items.sort(reverse=reverse)

        # Reorganizar itens na ordem
        for index, (val, item) in enumerate(items):
            tree.move(item, "", index)

        # Alternar direção da próxima ordenação
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def export_to_csv(self, tree):
        """Exporta os dados da TreeView para um arquivo CSV"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Escrever cabeçalhos
                    headers = [tree.heading(col)['text'] for col in tree['columns']]
                    writer.writerow(headers)

                    # Escrever dados
                    for item in tree.get_children():
                        values = tree.item(item)['values']
                        writer.writerow(values)

                messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")

    def clear_fields(self):
        """Limpa os campos de entrada"""
        if hasattr(self, "name_entry"):
            self.name_entry.delete(0, tk.END)
        if hasattr(self, "description_text"):
            self.description_text.delete("1.0", tk.END)
