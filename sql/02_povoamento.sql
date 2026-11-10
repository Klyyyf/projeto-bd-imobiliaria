-- ==========================================
-- Projeto de Banco de Dados - Imobiliária
-- Povoamento das tabelas (DML) - executar após 01_criacao.sql
-- ==========================================

PRAGMA foreign_keys = ON;

-- Clientes
INSERT INTO Cliente (cpf, nome, telefone) VALUES
('111.111.111-11', 'Daniel Luz', '(84) 99999-1111'),
('222.222.222-22', 'Maria Souza', '(84) 98888-2222'),
('555.555.555-55', 'Beatriz Medeiros', '(84) 99111-2233');

-- Proprietários
INSERT INTO Proprietario (cpf, nome, telefone) VALUES
('333.333.333-33', 'Luiz Feliciano', '(84) 97777-3333'),
('444.444.444-44', 'Klyfithon Paulo', '(84) 96666-4444');

-- Corretores (1 = Avaliador, 0 = Não avaliador)
INSERT INTO Corretor (creci, nome, telefone, avaliador) VALUES
('CRECI-1234', 'Carlos Eduardo', '(84) 95555-5555', 1),
('CRECI-5678', 'Fernanda Lima', '(84) 94444-4444', 0);

-- Imóveis (Tipos aceitos: 'Casa', 'Apartamento', 'Escritório', 'Comércio')
INSERT INTO Imovel (tipo, status, rua, numero, bairro, cidade, cep, preco, cpf_proprietario) VALUES
('Apartamento', 'Vendido', 'Av. Roberto Freire', 1000, 'Ponta Negra', 'Natal', '59090-000', 350000.00, '333.333.333-33'),
('Casa', 'Disponível', 'Rua das Dunas', 150, 'Capim Macio', 'Natal', '59078-000', 500000.00, '444.444.444-44'),
('Comércio', 'Disponível', 'Av. Afonso Pena', 400, 'Tirol', 'Natal', '59020-100', 750000.00, '333.333.333-33');

-- Visitas
INSERT INTO Visita (id_imovel, cpf_cliente, creci_corretor, data_visita, feedback) VALUES
(2, '111.111.111-11', 'CRECI-1234', '2026-10-25', 'Cliente demonstrou grande interesse na localização.');

-- Vendas (a comissão é calculada automaticamente pela coluna gerada)
INSERT INTO Venda (id_imovel, cpf_cliente, creci_corretor, valor_venda, percentual_comissao) VALUES
(1, '111.111.111-11', 'CRECI-1234', 340000.00, 5.0);
