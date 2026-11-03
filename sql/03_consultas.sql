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

-- 2. Comissão total por corretor (atributo derivado + GROUP BY)
SELECT cor.nome AS corretor, COUNT(v.id_venda) AS vendas,
       COALESCE(SUM(v.comissao), 0) AS comissao_total
FROM Corretor cor
LEFT JOIN Venda v ON v.creci_corretor = cor.creci
GROUP BY cor.creci, cor.nome
ORDER BY comissao_total DESC;

-- 3. Imóveis por proprietário (relacionamento Dono_do 1:N)
SELECT p.nome AS proprietario, COUNT(i.id_imovel) AS qtd_imoveis,
       COALESCE(SUM(i.preco), 0) AS valor_total
FROM Proprietario p
LEFT JOIN Imovel i ON i.cpf_proprietario = p.cpf
GROUP BY p.cpf, p.nome
ORDER BY qtd_imoveis DESC;

-- 4. Imóveis ainda disponíveis (não vendidos)
SELECT i.id_imovel, i.tipo, i.rua, i.numero, i.bairro, i.preco
FROM Imovel i
WHERE NOT EXISTS (SELECT 1 FROM Venda v WHERE v.id_imovel = i.id_imovel)
ORDER BY i.preco;

-- 5. Corretores contratados por cada proprietário (Contrata_o N:N)
SELECT p.nome AS proprietario, cor.nome AS corretor,
       CASE WHEN cor.avaliador = 1 THEN 'Sim' ELSE 'Não' END AS avaliador
FROM Contrata_o ct
JOIN Proprietario p ON p.cpf = ct.cpf_proprietario
JOIN Corretor cor   ON cor.creci = ct.creci_corretor
ORDER BY p.nome;

-- 6. Clientes atendidos por corretor (Compra_do N:N)
SELECT cor.nome AS corretor, COUNT(cd.cpf_cliente) AS clientes_atendidos
FROM Corretor cor
LEFT JOIN Compra_do cd ON cd.creci_corretor = cor.creci
GROUP BY cor.creci, cor.nome
ORDER BY clientes_atendidos DESC;
