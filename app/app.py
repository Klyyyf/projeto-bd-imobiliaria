"""CRUD simples da Imobiliária (Projeto de BD - UFRN).

Todo acesso ao banco é feito com SQL puro (sqlite3), e o último comando
executado aparece na tela para ser mostrado na apresentação.

Na primeira execução o arquivo imobiliaria.db é criado a partir de
../sql/01_criacao.sql e ../sql/02_povoamento.sql. As consultas da página
"Consultas" são lidas de ../sql/03_consultas.sql.
"""
import re
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for

BASE = Path(__file__).parent
PASTA_SQL = BASE.parent / "sql"
ARQUIVO_DB = BASE / "imobiliaria.db"

app = Flask(__name__)
app.secret_key = "projeto-bd"


# --------------------------------------------------------------------------
# Mapeamento das tabelas do esquema (sql/01_criacao.sql)
# --------------------------------------------------------------------------
TIPOS_IMOVEL = ["Casa", "Apartamento", "Escritório", "Comércio"]
STATUS_IMOVEL = ["Disponível", "Reservado", "Vendido"]

OPCOES_CLIENTE = "SELECT cpf AS valor, nome || ' (' || cpf || ')' AS rotulo FROM Cliente ORDER BY nome"
OPCOES_PROPRIETARIO = "SELECT cpf AS valor, nome || ' (' || cpf || ')' AS rotulo FROM Proprietario ORDER BY nome"
OPCOES_CORRETOR = "SELECT creci AS valor, nome || ' (' || creci || ')' AS rotulo FROM Corretor ORDER BY nome"
OPCOES_IMOVEL = ("SELECT id_imovel AS valor, '#' || id_imovel || ' - ' || tipo || ', ' || rua || ', ' || numero"
                 " || ' (' || status || ')' AS rotulo FROM Imovel ORDER BY id_imovel")
# Na venda só aparecem imóveis disponíveis (mais o já escolhido, ao editar)
OPCOES_IMOVEL_VENDA = ("SELECT id_imovel AS valor, '#' || id_imovel || ' - ' || tipo || ', ' || rua || ', ' || numero"
                       " AS rotulo FROM Imovel WHERE status = 'Disponível' OR id_imovel = :atual ORDER BY id_imovel")

ENTIDADES = {
    "clientes": {
        "titulo": "Clientes",
        "tabela": "Cliente",
        "pk": ["cpf"],
        "campos": [
            {"nome": "cpf", "rotulo": "CPF", "tipo": "text"},
            {"nome": "nome", "rotulo": "Nome", "tipo": "text"},
            {"nome": "telefone", "rotulo": "Telefone", "tipo": "text"},
        ],
    },
    "proprietarios": {
        "titulo": "Proprietários",
        "tabela": "Proprietario",
        "pk": ["cpf"],
        "campos": [
            {"nome": "cpf", "rotulo": "CPF", "tipo": "text"},
            {"nome": "nome", "rotulo": "Nome", "tipo": "text"},
            {"nome": "telefone", "rotulo": "Telefone", "tipo": "text"},
        ],
    },
    "corretores": {
        "titulo": "Corretores",
        "tabela": "Corretor",
        "pk": ["creci"],
        "campos": [
            {"nome": "creci", "rotulo": "CRECI", "tipo": "text"},
            {"nome": "nome", "rotulo": "Nome", "tipo": "text"},
            {"nome": "telefone", "rotulo": "Telefone", "tipo": "text"},
            {"nome": "avaliador", "rotulo": "Atua como avaliador", "tipo": "bool"},
        ],
        "sql_lista": """
            SELECT creci, nome, telefone,
                   CASE WHEN avaliador = 1 THEN 'Sim' ELSE 'Não' END AS avaliador
            FROM Corretor ORDER BY nome""",
    },
    "imoveis": {
        "titulo": "Imóveis",
        "tabela": "Imovel",
        "pk": ["id_imovel"],
        "pk_auto": True,
        "campos": [
            {"nome": "tipo", "rotulo": "Tipo", "tipo": "select", "opcoes": TIPOS_IMOVEL},
            {"nome": "status", "rotulo": "Status", "tipo": "select", "opcoes": STATUS_IMOVEL},
            {"nome": "rua", "rotulo": "Rua", "tipo": "text"},
            {"nome": "numero", "rotulo": "Número", "tipo": "int"},
            {"nome": "bairro", "rotulo": "Bairro", "tipo": "text"},
            {"nome": "cidade", "rotulo": "Cidade", "tipo": "text"},
            {"nome": "cep", "rotulo": "CEP", "tipo": "text"},
            {"nome": "preco", "rotulo": "Preço (R$)", "tipo": "number"},
            {"nome": "cpf_proprietario", "rotulo": "Proprietário", "tipo": "fk", "sql_opcoes": OPCOES_PROPRIETARIO},
        ],
        "sql_lista": """
            SELECT i.id_imovel, i.tipo, i.status, i.rua, i.numero, i.bairro, i.cidade, i.cep, i.preco,
                   p.nome AS proprietario
            FROM Imovel i
            JOIN Proprietario p ON p.cpf = i.cpf_proprietario
            ORDER BY i.id_imovel""",
    },
    "vendas": {
        "titulo": "Vendas",
        "tabela": "Venda",
        "pk": ["id_venda"],
        "pk_auto": True,
        "fixos": ["id_imovel"],  # o imóvel da venda não muda na edição
        # Ao vender, o imóvel passa a 'Vendido'; ao excluir a venda, volta a 'Disponível'
        "apos_inserir": "UPDATE Imovel SET status = 'Vendido' WHERE id_imovel = :id_imovel",
        "antes_excluir": """
            UPDATE Imovel SET status = 'Disponível'
            WHERE id_imovel = (SELECT id_imovel FROM Venda WHERE id_venda = :pk_id_venda)""",
        "campos": [
            {"nome": "id_imovel", "rotulo": "Imóvel", "tipo": "fk", "sql_opcoes": OPCOES_IMOVEL_VENDA},
            {"nome": "cpf_cliente", "rotulo": "Cliente (comprador)", "tipo": "fk", "sql_opcoes": OPCOES_CLIENTE},
            {"nome": "creci_corretor", "rotulo": "Corretor", "tipo": "fk", "sql_opcoes": OPCOES_CORRETOR},
            {"nome": "valor_venda", "rotulo": "Valor da venda (R$)", "tipo": "number"},
            {"nome": "percentual_comissao", "rotulo": "Comissão (%)", "tipo": "number"},
        ],
        "sql_lista": """
            SELECT v.id_venda, i.tipo || ', ' || i.rua AS imovel, c.nome AS cliente,
                   cor.nome AS corretor, v.valor_venda, v.percentual_comissao AS "comissao_%",
                   v.comissao
            FROM Venda v
            JOIN Imovel i     ON i.id_imovel = v.id_imovel
            JOIN Cliente c    ON c.cpf = v.cpf_cliente
            JOIN Corretor cor ON cor.creci = v.creci_corretor
            ORDER BY v.id_venda""",
    },
    "visitas": {
        "titulo": "Visitas",
        "tabela": "Visita",
        "pk": ["id_visita"],
        "pk_auto": True,
        "campos": [
            {"nome": "id_imovel", "rotulo": "Imóvel", "tipo": "fk", "sql_opcoes": OPCOES_IMOVEL},
            {"nome": "cpf_cliente", "rotulo": "Cliente", "tipo": "fk", "sql_opcoes": OPCOES_CLIENTE},
            {"nome": "creci_corretor", "rotulo": "Corretor", "tipo": "fk", "sql_opcoes": OPCOES_CORRETOR},
            {"nome": "data_visita", "rotulo": "Data da visita", "tipo": "date"},
            {"nome": "feedback", "rotulo": "Feedback", "tipo": "text", "opcional": True},
        ],
        "sql_lista": """
            SELECT vi.id_visita, vi.data_visita, i.tipo || ', ' || i.rua AS imovel,
                   c.nome AS cliente, cor.nome AS corretor, vi.feedback
            FROM Visita vi
            JOIN Imovel i     ON i.id_imovel = vi.id_imovel
            JOIN Cliente c    ON c.cpf = vi.cpf_cliente
            JOIN Corretor cor ON cor.creci = vi.creci_corretor
            ORDER BY vi.data_visita DESC""",
    },
    "contratacoes": {
        "titulo": "Contratações",
        "tabela": "Contrata_o",
        "pk": ["cpf_proprietario", "creci_corretor"],
        "editavel": False,  # tabela só de chaves: cadastra ou exclui
        "campos": [
            {"nome": "cpf_proprietario", "rotulo": "Proprietário", "tipo": "fk", "sql_opcoes": OPCOES_PROPRIETARIO},
            {"nome": "creci_corretor", "rotulo": "Corretor", "tipo": "fk", "sql_opcoes": OPCOES_CORRETOR},
        ],
        "sql_lista": """
            SELECT ct.cpf_proprietario, p.nome AS proprietario, ct.creci_corretor, cor.nome AS corretor
            FROM Contrata_o ct
            JOIN Proprietario p ON p.cpf = ct.cpf_proprietario
            JOIN Corretor cor   ON cor.creci = ct.creci_corretor
            ORDER BY p.nome""",
    },
    "atendimentos": {
        "titulo": "Atendimentos",
        "tabela": "Compra_do",
        "pk": ["cpf_cliente", "creci_corretor"],
        "editavel": False,
        "campos": [
            {"nome": "cpf_cliente", "rotulo": "Cliente", "tipo": "fk", "sql_opcoes": OPCOES_CLIENTE},
            {"nome": "creci_corretor", "rotulo": "Corretor", "tipo": "fk", "sql_opcoes": OPCOES_CORRETOR},
        ],
        "sql_lista": """
            SELECT cd.cpf_cliente, c.nome AS cliente, cd.creci_corretor, cor.nome AS corretor
            FROM Compra_do cd
            JOIN Cliente c    ON c.cpf = cd.cpf_cliente
            JOIN Corretor cor ON cor.creci = cd.creci_corretor
            ORDER BY c.nome""",
    },
}

SEPARADOR_CHAVE = "~"  # chaves compostas viram "valor1~valor2" na URL


# --------------------------------------------------------------------------
# Acesso ao banco
# --------------------------------------------------------------------------
def conectar():
    conn = sqlite3.connect(ARQUIVO_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def executar(sql, params=None, mostrar=True):
    """Executa um comando SQL e, se `mostrar`, exibe-o na próxima página."""
    return executar_transacao([(sql, params)], mostrar)


def executar_transacao(comandos, mostrar=True):
    """Executa vários comandos numa única transação (tudo ou nada)."""
    executados, linhas = [], []
    with conectar() as conn:
        for sql, params in comandos:
            sql = " ".join(sql.split())
            linhas = [dict(l) for l in conn.execute(sql, params or {}).fetchall()]
            executados.append({"sql": sql, "params": params or {}})
    if mostrar:
        for comando in executados:
            flash(comando, "sql")
    return linhas


def inicializar_banco():
    """Cria e popula o banco na primeira execução."""
    if ARQUIVO_DB.exists():
        return
    script = "".join((PASTA_SQL / f).read_text("utf-8") for f in ("01_criacao.sql", "02_povoamento.sql"))
    with conectar() as conn:
        conn.executescript(script)


def carregar_consultas():
    """Lê os blocos '-- N. Título' + comando de sql/03_consultas.sql."""
    texto = (PASTA_SQL / "03_consultas.sql").read_text("utf-8")
    return re.findall(r"^--\s*\d+\.\s*(.+?)\n(.*?;)", texto, re.S | re.M)


inicializar_banco()


def get_entidade(nome):
    if nome not in ENTIDADES:
        abort(404)
    return ENTIDADES[nome]


def chave_da_linha(ent, linha):
    return SEPARADOR_CHAVE.join(str(linha[c]) for c in ent["pk"])


def filtro_pk(ent, chave):
    valores = chave.split(SEPARADOR_CHAVE)
    if len(valores) != len(ent["pk"]):
        abort(404)
    where = " AND ".join(f"{c} = :pk_{c}" for c in ent["pk"])
    return where, {f"pk_{c}": v for c, v in zip(ent["pk"], valores)}


def ler_formulario(ent):
    valores = {}
    for campo in ent["campos"]:
        bruto = request.form.get(campo["nome"], "").strip()
        if campo["tipo"] == "bool":
            valores[campo["nome"]] = 1 if campo["nome"] in request.form else 0
        elif bruto == "":
            valores[campo["nome"]] = None
        elif campo["tipo"] == "int":
            valores[campo["nome"]] = int(bruto)
        elif campo["tipo"] == "number":
            valores[campo["nome"]] = float(bruto.replace(",", "."))
        else:
            valores[campo["nome"]] = bruto
    return valores


def opcoes_fk(ent, registro):
    return {
        c["nome"]: executar(c["sql_opcoes"], {"atual": registro.get(c["nome"])}, mostrar=False)
        for c in ent["campos"] if c["tipo"] == "fk"
    }


# --------------------------------------------------------------------------
# Rotas
# --------------------------------------------------------------------------
@app.context_processor
def menu():
    return {"entidades": ENTIDADES, "chave_da_linha": chave_da_linha}


@app.route("/")
def inicio():
    totais = {
        chave: executar(f"SELECT COUNT(*) AS n FROM {ent['tabela']}", mostrar=False)[0]["n"]
        for chave, ent in ENTIDADES.items()
    }
    return render_template("inicio.html", totais=totais)


@app.route("/<nome>")
def listar(nome):
    ent = get_entidade(nome)
    sql = ent.get("sql_lista") or f"SELECT * FROM {ent['tabela']}"
    linhas = executar(sql, mostrar=False)
    return render_template("lista.html", nome=nome, ent=ent, linhas=linhas,
                           sql_lista=" ".join(sql.split()))


@app.route("/<nome>/novo", methods=["GET", "POST"])
def criar(nome):
    ent = get_entidade(nome)
    registro = {}
    if request.method == "POST":
        registro = ler_formulario(ent)
        colunas = ", ".join(registro)
        marcadores = ", ".join(f":{c}" for c in registro)
        comandos = [(f"INSERT INTO {ent['tabela']} ({colunas}) VALUES ({marcadores})", registro)]
        if ent.get("apos_inserir"):
            comandos.append((ent["apos_inserir"], registro))
        try:
            executar_transacao(comandos)
            flash("Registro cadastrado com sucesso.", "ok")
            return redirect(url_for("listar", nome=nome))
        except sqlite3.Error as e:
            flash(f"Erro do banco: {e}", "erro")
    return render_template("form.html", nome=nome, ent=ent, registro=registro,
                           opcoes=opcoes_fk(ent, registro), editando=False)


@app.route("/<nome>/<chave>/editar", methods=["GET", "POST"])
def editar(nome, chave):
    ent = get_entidade(nome)
    if not ent.get("editavel", True):
        abort(404)
    where, params_pk = filtro_pk(ent, chave)
    travados = ent["pk"] + ent.get("fixos", [])
    if request.method == "POST":
        valores = {c: v for c, v in ler_formulario(ent).items() if c not in travados}
        atribuicoes = ", ".join(f"{c} = :{c}" for c in valores)
        try:
            executar(f"UPDATE {ent['tabela']} SET {atribuicoes} WHERE {where}", {**valores, **params_pk})
            flash("Registro atualizado.", "ok")
            return redirect(url_for("listar", nome=nome))
        except sqlite3.Error as e:
            flash(f"Erro do banco: {e}", "erro")
    achados = executar(f"SELECT * FROM {ent['tabela']} WHERE {where}", params_pk, mostrar=False)
    if not achados:
        abort(404)
    registro = achados[0]
    if request.method == "POST":
        registro.update(valores)  # mantém o que foi digitado quando dá erro
    return render_template("form.html", nome=nome, ent=ent, registro=registro,
                           opcoes=opcoes_fk(ent, registro), editando=True, travados=travados)


@app.route("/<nome>/<chave>/excluir", methods=["POST"])
def excluir(nome, chave):
    ent = get_entidade(nome)
    where, params_pk = filtro_pk(ent, chave)
    comandos = [(f"DELETE FROM {ent['tabela']} WHERE {where}", params_pk)]
    if ent.get("antes_excluir"):
        comandos.insert(0, (ent["antes_excluir"], params_pk))
    try:
        executar_transacao(comandos)
        flash("Registro excluído.", "ok")
    except sqlite3.Error as e:
        flash(f"Não foi possível excluir (restrição de integridade): {e}", "erro")
    return redirect(url_for("listar", nome=nome))


@app.route("/consultas")
def consultas():
    resultados = []
    for titulo, sql in carregar_consultas():
        try:
            linhas, erro = executar(sql, mostrar=False), None
        except sqlite3.Error as e:
            linhas, erro = [], str(e)
        resultados.append({"titulo": titulo, "sql": sql.strip(), "linhas": linhas, "erro": erro})
    return render_template("consultas.html", resultados=resultados)


if __name__ == "__main__":
    app.run(debug=True)
