-- Criando o banco de dados  
CREATE DATABASE db_biblioteca;

-- Utilizar/manipular db_biblioteca
USE db_biblioteca;

-- Criação das tabelas principais
-- Tabela de Livros
CREATE TABLE Livros (
    livro_id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    ano_publicacao INT,
    editora VARCHAR(100),
    quantidade_copias INT DEFAULT 0,
    localizacao_estante VARCHAR(50)
);

-- Tabela de Autores
CREATE TABLE Autores (
    autor_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    nacionalidade VARCHAR(50)
);

-- Tabela de relacionamento Livros-Autores (permite múltiplos autores por livro)
CREATE TABLE LivrosAutores (
    livro_id INT,
    autor_id INT,
    FOREIGN KEY (livro_id) REFERENCES Livros(livro_id),
    FOREIGN KEY (autor_id) REFERENCES Autores(autor_id),
    PRIMARY KEY (livro_id, autor_id)
);

-- Tabela de Usuários
CREATE TABLE Usuarios (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefone VARCHAR(20),
    data_cadastro DATE,
    status_usuario VARCHAR(20) DEFAULT 'Ativo'
);


-- Tabela de Endereço
CREATE TABLE Endereco (
	endereco_id INT PRIMARY KEY AUTO_INCREMENT,
    logradouro VARCHAR(100) NOT NULL,
    numero INT,
    complemento VARCHAR(100),
    bairro VARCHAR(50),
    cidade VARCHAR(50),
    estado VARCHAR(25),
    cep INT
);

-- Tabela UsuarioEndereço
CREATE TABLE UsuarioEndereco (
	usuario_id INT,
    endereco_id INT,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios (usuario_id),
    FOREIGN KEY (endereco_id) REFERENCES Endereco (endereco_id),
    PRIMARY KEY (usuario_id, endereco_id)
);

-- Tabela de Empréstimos
CREATE TABLE Emprestimos (
    emprestimo_id INT PRIMARY KEY AUTO_INCREMENT,
    livro_id INT,
    usuario_id INT,
    data_emprestimo DATE NOT NULL,
    data_devolucao_prevista DATE NOT NULL,
    data_devolucao_real DATE,
    status_emprestimo VARCHAR(20) DEFAULT 'Ativo',
    FOREIGN KEY (livro_id) REFERENCES Livros(livro_id),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(usuario_id)
);

-- Tabela de Categorias
CREATE TABLE Categorias (
    categoria_id INT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT
);

-- Tabela de relacionamento Livros-Categorias
CREATE TABLE LivrosCategorias (
    livro_id INT,
    categoria_id INT,
    FOREIGN KEY (livro_id) REFERENCES Livros(livro_id),
    FOREIGN KEY (categoria_id) REFERENCES Categorias(categoria_id),
    PRIMARY KEY (livro_id, categoria_id)
);

-- Tabela de Reservas
CREATE TABLE Reservas (
    reserva_id INT PRIMARY KEY AUTO_INCREMENT,
    livro_id INT,
    usuario_id INT,
    data_reserva DATE NOT NULL,
    status_reservas VARCHAR(20) DEFAULT 'Pendente',
    FOREIGN KEY (livro_id) REFERENCES Livros(livro_id),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(usuario_id)
);

-- Tabela de Multas
CREATE TABLE Multas (
    multa_id INT PRIMARY KEY AUTO_INCREMENT,
    emprestimo_id INT,
    valor DECIMAL(10,2) NOT NULL,
    status_multas VARCHAR(20) DEFAULT 'Devendo',
    data_geracao DATE NOT NULL,
    data_pagamento DATE,
    FOREIGN KEY (emprestimo_id) REFERENCES Emprestimos(emprestimo_id)
);
