-- ==========================================
-- Projeto de Banco de Dados - Imobiliária
-- Povoamento das tabelas (DML) - executar após 01_criacao.sql
-- ==========================================

PRAGMA foreign_keys = ON;

-- Clientes
INSERT INTO Cliente (cpf, nome, telefone) VALUES
('111.111.111-11', 'Daniel Luz', '(84) 99999-1111'),
('222.222.222-22', 'Maria Souza', '(84) 98888-2222'),
('555.555.555-55', 'Beatriz Medeiros', '(84) 99111-2233'),
('666.666.666-66', 'Lucas Silveira', '(84) 98222-3344'),
('777.777.777-77', 'Camila Albuquerque', '(84) 97333-5566'),
('888.888.888-88', 'Thiago Bezerra', '(84) 96444-7788');

-- Proprietários
INSERT INTO Proprietario (cpf, nome, telefone) VALUES
('333.333.333-33', 'Luiz Feliciano', '(84) 97777-3333'),
('444.444.444-44', 'Klyfithon Paulo', '(84) 96666-4444'),
('123.456.789-00', 'Roberto Guedes', '(84) 99888-1122'),
('234.567.890-11', 'Marcos Vinicius', '(84) 98777-2233'),
('345.678.901-22', 'Juliana Paiva', '(84) 97666-3344');

-- Corretores (1 = Avaliador, 0 = Não avaliador)
INSERT INTO Corretor (creci, nome, telefone, avaliador) VALUES
('CRECI-1234', 'Carlos Eduardo', '(84) 95555-5555', 1),
('CRECI-5678', 'Fernanda Lima', '(84) 94444-4444', 0),
('CRECI-9988', 'Juliana Azevedo', '(84) 95555-6677', 1),
('CRECI-4321', 'Marcos Paulo', '(84) 94444-3322', 1),
('CRECI-8765', 'Priscila Duarte', '(84) 93333-1100', 0);

-- Imóveis (Tipos aceitos: 'Casa', 'Apartamento', 'Escritório', 'Comércio')
INSERT INTO Imovel (tipo, rua, numero, bairro, cidade, cep, preco, cpf_proprietario) VALUES
('Apartamento', 'Av. Roberto Freire', 1000, 'Ponta Negra', 'Natal', '59090-000', 350000.00, '333.333.333-33'),
('Casa', 'Rua das Dunas', 150, 'Capim Macio', 'Natal', '59078-000', 500000.00, '444.444.444-44'),
('Casa', 'Rua Engenheiro Roberto Freire', 450, 'Petrópolis', 'Natal', '59012-000', 680000.00, '123.456.789-00'),
('Escritório', 'Av. Afonso Pena', 700, 'Tirol', 'Natal', '59020-100', 290000.00, '234.567.890-11'),
('Comércio', 'Rua dos Eucaliptos', 12, 'Candelária', 'Natal', '59066-120', 850000.00, '345.678.901-22'),
('Apartamento', 'Av. Hermes da Fonseca', 1200, 'Tirol', 'Natal', '59020-555', 420000.00, '123.456.789-00'),
('Casa', 'Rua Praia de Genipabu', 85, 'Ponta Negra', 'Natal', '59092-100', 530000.00, '234.567.890-11');

-- Contratações (Proprietário x Corretor)
INSERT INTO Contrata_o (cpf_proprietario, creci_corretor) VALUES
('333.333.333-33', 'CRECI-1234'),
('444.444.444-44', 'CRECI-5678'),
('123.456.789-00', 'CRECI-9988'),
('234.567.890-11', 'CRECI-4321'),
('345.678.901-22', 'CRECI-8765');

-- Atendimentos / Associações (Cliente x Corretor)
INSERT INTO Compra_do (cpf_cliente, creci_corretor) VALUES
('111.111.111-11', 'CRECI-1234'),
('222.222.222-22', 'CRECI-5678'),
('555.555.555-55', 'CRECI-9988'),
('666.666.666-66', 'CRECI-4321'),
('777.777.777-77', 'CRECI-8765'),
('888.888.888-88', 'CRECI-9988');

-- Vendas (a comissão é calculada automaticamente pela coluna gerada)
INSERT INTO Venda (id_imovel, cpf_cliente, creci_corretor, valor_venda, percentual_comissao) VALUES
(1, '111.111.111-11', 'CRECI-1234', 340000.00, 5.0),
(3, '555.555.555-55', 'CRECI-9988', 650000.00, 6.0),
(4, '666.666.666-66', 'CRECI-4321', 280000.00, 5.0),
(5, '777.777.777-77', 'CRECI-8765', 830000.00, 5.5),
(6, '888.888.888-88', 'CRECI-9988', 410000.00, 5.0);
