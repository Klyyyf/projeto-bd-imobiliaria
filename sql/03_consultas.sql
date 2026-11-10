-- ==========================================
-- Projeto de Banco de Dados - Imobiliária
-- Exemplos de utilização do banco (consultas)
-- ==========================================

-- 1. Relatório de vendas (Venda + Cliente + Proprietário + Corretor + Imóvel)
SELECT v.id_venda, c.nome AS cliente, p.nome AS proprietario, cor.nome AS corretor,
       i.tipo AS tipo_imovel, i.bairro, v.valor_venda,
       v.percentual_comissao || '%' AS taxa, v.comissao
FROM Venda v
JOIN Cliente c      ON v.cpf_cliente = c.cpf
JOIN Corretor cor   ON v.creci_corretor = cor.creci
JOIN Imovel i       ON v.id_imovel = i.id_imovel
JOIN Proprietario p ON i.cpf_proprietario = p.cpf;

-- 2. Vendas e comissão total por corretor (atributo derivado + GROUP BY)
SELECT cor.nome AS corretor, COUNT(v.id_venda) AS total_vendas,
       COALESCE(SUM(v.comissao), 0) AS comissao_total
FROM Corretor cor
LEFT JOIN Venda v ON v.creci_corretor = cor.creci
GROUP BY cor.creci, cor.nome
ORDER BY comissao_total DESC;

-- 3. Imóveis disponíveis para venda
SELECT i.id_imovel, i.tipo, i.rua, i.numero, i.bairro, i.preco, p.nome AS proprietario
FROM Imovel i
JOIN Proprietario p ON i.cpf_proprietario = p.cpf
WHERE i.status = 'Disponível'
ORDER BY i.preco;

-- 4. Histórico de visitas (Visita + Imóvel + Cliente + Corretor)
SELECT vi.data_visita, i.tipo || ', ' || i.rua AS imovel, i.status,
       c.nome AS cliente, cor.nome AS corretor, vi.feedback
FROM Visita vi
JOIN Imovel i     ON i.id_imovel = vi.id_imovel
JOIN Cliente c    ON c.cpf = vi.cpf_cliente
JOIN Corretor cor ON cor.creci = vi.creci_corretor
ORDER BY vi.data_visita DESC;

-- 5. Quantidade de imóveis por bairro
SELECT bairro, COUNT(*) AS quantidade
FROM Imovel
GROUP BY bairro
ORDER BY quantidade DESC;

-- 6. Preço médio por tipo de imóvel
SELECT tipo, COUNT(*) AS quantidade, ROUND(AVG(preco), 2) AS preco_medio
FROM Imovel
GROUP BY tipo
ORDER BY preco_medio DESC;

-- 7. Imóveis por proprietário (relacionamento Dono_do 1:N)
SELECT p.nome AS proprietario, COUNT(i.id_imovel) AS qtd_imoveis,
       COALESCE(SUM(i.preco), 0) AS valor_total
FROM Proprietario p
LEFT JOIN Imovel i ON i.cpf_proprietario = p.cpf
GROUP BY p.cpf, p.nome
ORDER BY qtd_imoveis DESC;
