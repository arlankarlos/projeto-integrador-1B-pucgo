# Projeto Integrador - CRUD-Py-Tkinter
### Pontifícia Universidade Católica de Goiás - PUC Goiás [![PUC-GO](https://img.shields.io/badge/PUCGO-blue?style=plastic&link=https%3A%2F%2Fwww.pucgoias.edu.br%2F)](https://www.pucgoias.edu.br/)

#### Curso: Big Data e Inteligência Artificial
#### Professor: Thalles Bruno G. N. dos Santos  
#### Disciplina: Projeto Integrador I-B
#### Aluno: Arlan Karlos Gouveia do Nascimento


### Bibliotecas Necessárias
tkcalendar==1.6.1
python-dotenv==1.0.0
mysql-connector-python==8.1.0
```
pip install -r requirements.txt
```

Criar arquivo .env:

```
DB_HOST='localhost'
DB_USER='root'
DB_PASSWORD='root' # sua senha mysql
DB_NAME='db_biblioteca'
```

## Descrição

O programa é um sistema de gerenciamento de biblioteca que permite a administração de usuários, livros, autores, categorias, empréstimos e reservas. Ele utiliza uma interface gráfica construída com `tkinter` para interagir com o usuário e um banco de dados para armazenar as informações.


### Funcionalidades Principais

1. **Gerenciamento de Usuários**:
   - **Criação de Usuários**: Permite criar novos usuários com informações como nome, email, telefone e endereço.
   - **Atualização de Usuários**: Permite atualizar as informações dos usuários existentes.
   - **Exclusão de Usuários**: Permite excluir usuários do sistema.
   - **Visualização de Usuários**: Exibe uma lista de todos os usuários cadastrados e permite visualizar detalhes específicos de cada usuário.

2. **Gerenciamento de Livros**:
   - **Criação de Livros**: Permite adicionar novos livros ao sistema, incluindo informações como título, ISBN, ano de publicação, editora, quantidade de cópias e localização na estante.
   - **Atualização de Livros**: Permite atualizar as informações dos livros existentes.
   - **Exclusão de Livros**: Permite excluir livros do sistema.
   - **Visualização de Livros**: Exibe uma lista de todos os livros cadastrados e permite visualizar detalhes específicos de cada livro.
   - **Exportação para CSV**: Permite exportar a lista de livros para um arquivo CSV.

3. **Gerenciamento de Autores**:
   - **Criação de Autores**: Permite adicionar novos autores ao sistema.
   - **Atualização de Autores**: Permite atualizar as informações dos autores existentes.
   - **Visualização de Autores**: Exibe uma lista de todos os autores cadastrados e permite visualizar detalhes específicos de cada autor.

4. **Gerenciamento de Categorias**:
   - **Criação de Categorias**: Permite adicionar novas categorias ao sistema.
   - **Atualização de Categorias**: Permite atualizar as informações das categorias existentes.
   - **Visualização de Categorias**: Exibe uma lista de todas as categorias cadastradas.

5. **Gerenciamento de Empréstimos**:
   - **Realização de Empréstimos**: Permite registrar novos empréstimos de livros para os usuários.
   - **Devolução de Livros**: Permite registrar a devolução de livros emprestados.
   - **Visualização de Empréstimos**: Exibe uma lista de todos os empréstimos realizados e permite visualizar detalhes específicos de cada empréstimo.

6. **Gerenciamento de Reservas**:
   - **Realização de Reservas**: Permite registrar reservas de livros para os usuários.
   - **Visualização de Reservas**: Exibe uma lista de todas as reservas realizadas e permite visualizar detalhes específicos de cada reserva.

7. **Gerenciamento de Multas**:
   - **Visualização de Multas**: Exibe uma lista de todas as multas geradas e permite visualizar detalhes específicos de cada multa.
   - **Processamento de Pagamento de Multas**: Permite registrar o pagamento de multas.

### Estrutura do Projeto
- **main.py**: Ponto de entrada do programa que inicializa a interface gráfica.
- **interface.py**: Contém a classe `UserManagementInterface` que gerencia a interface gráfica e as funcionalidades relacionadas aos usuários. Gerencia o Menu e o contexto geral do aplicativo integrando as demais interfaces.
- **interface_books.py**: Contém a classe `BooksManagementInterface` que gerencia a interface gráfica e as funcionalidades relacionadas aos livros.
- **interface_author.py**: Contém a classe `AuthorManagementInterface` que gerencia a interface gráfica e as funcionalidades relacionadas aos autores.
- **interface_categories.py**: Contém a classe `CategoriesManagementInterface` que gerencia a interface gráfica e as funcionalidades relacionadas às categorias.
- **interface_borrow.py**: Contém a classe `BorrowManagementInterface` que gerencia a interface gráfica e as funcionalidades relacionadas aos empréstimos e reservas.
- **create_user.py**: Contém funções auxiliares para criar usuários no banco de dados.
- **read_update_delete_user.py**: Contém funções auxiliares para ler, atualizar e deletar usuários no banco de dados.
- **add_to_inventory.py**: Contém funções auxiliares para adicionar livros, autores e categorias ao banco de dados. Estrutura inutilizada após realização da aplicação gráfica com tkinter.
- **db_utils.py**: Contém funções utilitárias para interagir com o banco de dados.
- **validate_utils.py**: Contém funções para validar dados de entrada, como email, telefone, CEP, etc.





## Tecnologias
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=for-the-badge&logo=anaconda&logoColor=white)  ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) 



### Licença
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)