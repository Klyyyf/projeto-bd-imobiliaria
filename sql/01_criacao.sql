-- ==========================================
-- Projeto de Banco de Dados - Imobiliária
-- Criação do esquema relacional (DDL) - SQLite
-- ==========================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Venda;
DROP TABLE IF EXISTS Compra_do;
DROP TABLE IF EXISTS Contrata_o;
DROP TABLE IF EXISTS Imovel;
DROP TABLE IF EXISTS Corretor;
DROP TABLE IF EXISTS Proprietario;
DROP TABLE IF EXISTS Cliente;

-- Tabela Cliente (Chave Primária: CPF)
CREATE TABLE Cliente (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL
);

-- Tabela Proprietário (Chave Primária: CPF)
CREATE TABLE Proprietario (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL
);

-- Tabela Corretor (Chave Primária: CRECI)
-- 'avaliador' mapeia se atua ou não como avaliador (0 = Não, 1 = Sim)
CREATE TABLE Corretor (
    creci TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    avaliador INTEGER NOT NULL CHECK (avaliador IN (0, 1))
);

-- Tabela Imóvel (Com endereço composto e restrição de tipos)
CREATE TABLE Imovel (
    id_imovel INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('Casa', 'Apartamento', 'Escritório', 'Comércio')),
    rua TEXT NOT NULL,
    numero INTEGER NOT NULL,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    cep TEXT NOT NULL,
    preco REAL NOT NULL,
    cpf_proprietario TEXT NOT NULL,
    FOREIGN KEY (cpf_proprietario) REFERENCES Proprietario(cpf) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabela Contrata_o (Proprietário contrata Corretor)
CREATE TABLE Contrata_o (
    cpf_proprietario TEXT NOT NULL,
    creci_corretor TEXT NOT NULL,
    PRIMARY KEY (cpf_proprietario, creci_corretor),
    FOREIGN KEY (cpf_proprietario) REFERENCES Proprietario(cpf) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (creci_corretor) REFERENCES Corretor(creci) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabela Compra_do (Cliente busca/associa-se ao Corretor)
CREATE TABLE Compra_do (
    cpf_cliente TEXT NOT NULL,
    creci_corretor TEXT NOT NULL,
    PRIMARY KEY (cpf_cliente, creci_corretor),
    FOREIGN KEY (cpf_cliente) REFERENCES Cliente(cpf) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (creci_corretor) REFERENCES Corretor(creci) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabela Venda (Representa a negociação intermediada)
-- O campo 'comissao' é um atributo derivado calculado automaticamente
CREATE TABLE Venda (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_imovel INTEGER UNIQUE NOT NULL,
    cpf_cliente TEXT NOT NULL,
    creci_corretor TEXT NOT NULL,
    valor_venda REAL NOT NULL,
    percentual_comissao REAL NOT NULL DEFAULT 5.0,
    comissao REAL GENERATED ALWAYS AS (valor_venda * percentual_comissao / 100.0) STORED,
    FOREIGN KEY (id_imovel) REFERENCES Imovel(id_imovel) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (cpf_cliente) REFERENCES Cliente(cpf) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (creci_corretor) REFERENCES Corretor(creci) ON DELETE RESTRICT ON UPDATE CASCADE
);
