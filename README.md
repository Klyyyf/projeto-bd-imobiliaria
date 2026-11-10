# Projeto de Banco de Dados — Imobiliária

Projeto da disciplina de Banco de Dados (BTI - UFRN).

**Alunos:** Luiz Feliciano, Klyfithon Paulo, Daniel Luz

O sistema modela o funcionamento de uma imobiliária, controlando clientes, proprietários,
corretores, imóveis e as vendas intermediadas pelos corretores (com cálculo de comissão).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| [`docs/`](docs/) | Minimundo, justificativa da modelagem e Diagrama ER (iteração 1) |
| [`sql/01_criacao.sql`](sql/01_criacao.sql) | Criação das tabelas (DDL) |
| [`sql/02_povoamento.sql`](sql/02_povoamento.sql) | Povoamento das tabelas (DML) |
| [`sql/03_consultas.sql`](sql/03_consultas.sql) | Exemplos de consultas |
| [`notebook/`](notebook/) | Notebook do Google Colab com a criação e testes do banco |
| [`app/`](app/) | Aplicação web (CRUD) para demonstrar o uso do banco |

## Esquema relacional

- **Cliente** (<u>cpf</u>, nome, telefone)
- **Proprietario** (<u>cpf</u>, nome, telefone)
- **Corretor** (<u>creci</u>, nome, telefone, avaliador)
- **Imovel** (<u>id_imovel</u>, tipo, status, rua, numero, bairro, cidade, cep, preco, cpf_proprietario → Proprietario)
- **Contrata_o** (<u>cpf_proprietario → Proprietario, creci_corretor → Corretor</u>)
- **Compra_do** (<u>cpf_cliente → Cliente, creci_corretor → Corretor</u>)
- **Venda** (<u>id_venda</u>, id_imovel → Imovel, cpf_cliente → Cliente, creci_corretor → Corretor,
  valor_venda, percentual_comissao, comissao)
- **Visita** (<u>id_visita</u>, id_imovel → Imovel, cpf_cliente → Cliente, creci_corretor → Corretor,
  data_visita, feedback)

`comissao` é um atributo derivado, calculado pelo próprio banco
(`GENERATED ALWAYS AS (valor_venda * percentual_comissao / 100.0)`).

## Criando o banco manualmente

Com o [SQLite](https://sqlite.org/download.html) instalado:

```bash
sqlite3 imobiliaria.db < sql/01_criacao.sql
sqlite3 imobiliaria.db < sql/02_povoamento.sql
sqlite3 imobiliaria.db < sql/03_consultas.sql
```

Ou abra o notebook em `notebook/Projeto_BD_V3.ipynb` no Google Colab.

## Rodando a aplicação

Requer Python 3.10+.

```bash
cd app
pip install -r requirements.txt
python app.py
```

Acesse http://localhost:5000.

Na primeira execução o arquivo `app/imobiliaria.db` é criado automaticamente a partir de
`sql/01_criacao.sql` e `sql/02_povoamento.sql`. Para voltar aos dados iniciais, basta apagar esse arquivo.

### Funcionalidades

- Cadastro, listagem, edição e exclusão de Clientes, Proprietários, Corretores, Imóveis, Vendas e Visitas.
- Ao registrar uma venda, o imóvel passa automaticamente para o status `Vendido` (na mesma transação);
  ao excluir a venda, ele volta a `Disponível`. Só imóveis disponíveis aparecem no cadastro de venda.
- Cadastro e exclusão das associações Contrata_o (Contratações) e Compra_do (Atendimentos).
- Cada comando `INSERT`, `UPDATE` ou `DELETE` executado é exibido na tela.
- Erros de restrição (chave estrangeira, `UNIQUE`, `CHECK`) são mostrados ao usuário — por exemplo,
  não é possível vender o mesmo imóvel duas vezes nem excluir um cliente que possui venda.
- Página **Consultas** executando os comandos de `sql/03_consultas.sql`.
