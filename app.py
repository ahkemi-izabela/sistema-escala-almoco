from flask import Flask, render_template, request, redirect, session
from database import conectar

app = Flask(__name__)
app.secret_key = "sistema_escala"

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND senha = %s",
            (email, senha)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if not usuario:
            return "E-mail ou senha incorretos"

        session["usuario"] = usuario["email"]
        session["tipo"] = usuario["tipo"]

        if usuario["tipo"] == "admin":
            return redirect("/dashboard")
        else:
            return redirect("/dashboard_funcionario")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM funcionarios")
    total_funcionarios = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM horarios")
    total_horarios = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM escala_almoco")
    total_escalas = cursor.fetchone()["total"]

    cursor.close()
    conexao.close()

    return render_template(
        "dashboard.html",
        total_funcionarios=total_funcionarios,
        total_horarios=total_horarios,
        total_escalas=total_escalas
    )


@app.route("/funcionarios", methods=["GET", "POST"])
def funcionarios():
    if "usuario" not in session:
        return redirect("/")

    if session.get("tipo") != "admin":
        return "Acesso negado. Apenas administradores podem acessar esta página."

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        setor = request.form["setor"]
        cargo = request.form["cargo"]

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute(
            "INSERT INTO funcionarios (nome, email, setor, cargo) VALUES (%s, %s, %s, %s)",
            (nome, email, setor, cargo)
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        return redirect("/funcionarios")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM funcionarios")
    lista_funcionarios = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "funcionarios.html",
        funcionarios=lista_funcionarios
    )
@app.route("/excluir_funcionario/<int:id>")
def excluir_funcionario(id):
    if "usuario" not in session:
        return redirect("/")

    if session.get("tipo") != "admin":
        return "Acesso negado. Apenas administradores podem acessar esta página."

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM funcionarios WHERE id = %s",
        (id,)
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect("/funcionarios")
@app.route("/editar_funcionario/<int:id>", methods=["GET", "POST"])
def editar_funcionario(id):
    if "usuario" not in session:
        return redirect("/")

    if session.get("tipo") != "admin":
        return "Acesso negado. Apenas administradores podem acessar esta página."

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        setor = request.form["setor"]
        cargo = request.form["cargo"]

        cursor.execute(
            "UPDATE funcionarios SET nome = %s, email = %s, setor = %s, cargo = %s WHERE id = %s",
            (nome, email, setor, cargo, id)
        )

        conexao.commit()
        cursor.close()
        conexao.close()

        return redirect("/funcionarios")

    cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (id,))
    funcionario = cursor.fetchone()

    cursor.close()
    conexao.close()

    return render_template("editar_funcionario.html", funcionario=funcionario)
@app.route("/horarios", methods=["GET", "POST"])
def horarios():
    if "usuario" not in session:
        return redirect("/")

    if session.get("tipo") != "admin":
        return "Acesso negado. Apenas administradores podem acessar esta página."

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    if request.method == "POST":
        horario_inicio = request.form["horario_inicio"]
        horario_fim = request.form["horario_fim"]
        limite = request.form["limite"]

        cursor.execute(
            "INSERT INTO horarios (horario_inicio, horario_fim, limite_funcionarios) VALUES (%s, %s, %s)",
            (horario_inicio, horario_fim, limite)
        )

        conexao.commit()

        cursor.close()
        conexao.close()

        return redirect("/horarios")

    cursor.execute("SELECT * FROM horarios")
    lista_horarios = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "horarios.html",
        horarios=lista_horarios
    )

@app.route("/escala", methods=["GET", "POST"])
def escala():
    if "usuario" not in session:
        return redirect("/")

    if session.get("tipo") != "admin":
        return "Acesso negado. Apenas administradores podem acessar esta página."

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    if request.method == "POST":
        funcionario_id = request.form["funcionario_id"]
        horario_id = request.form["horario_id"]
        data = request.form["data"]

        cursor.execute(
            "INSERT INTO escala_almoco (funcionario_id, horario_id, data) VALUES (%s, %s, %s)",
            (funcionario_id, horario_id, data)
        )

        conexao.commit()

        return redirect("/escala")

    cursor.execute("SELECT * FROM funcionarios")
    funcionarios = cursor.fetchall()

    cursor.execute("SELECT * FROM horarios")
    horarios = cursor.fetchall()

    cursor.execute("""
        SELECT 
            escala_almoco.id,
            funcionarios.nome,
            horarios.horario_inicio,
            horarios.horario_fim,
            escala_almoco.data
        FROM escala_almoco
        JOIN funcionarios ON escala_almoco.funcionario_id = funcionarios.id
        JOIN horarios ON escala_almoco.horario_id = horarios.id
    """)

    escalas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "escala.html",
        funcionarios=funcionarios,
        horarios=horarios,
        escalas=escalas
    )
@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect("/")

@app.route("/relatorio_escala", methods=["GET", "POST"])
def relatorio_escala():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    data_filtro = request.form.get("data_filtro")

    if data_filtro:
        cursor.execute("""
            SELECT 
                funcionarios.nome,
                funcionarios.setor,
                funcionarios.cargo,
                horarios.horario_inicio,
                horarios.horario_fim,
                escala_almoco.data
            FROM escala_almoco
            JOIN funcionarios ON escala_almoco.funcionario_id = funcionarios.id
            JOIN horarios ON escala_almoco.horario_id = horarios.id
            WHERE escala_almoco.data = %s
            ORDER BY horarios.horario_inicio
        """, (data_filtro,))
    else:
        cursor.execute("""
            SELECT 
                funcionarios.nome,
                funcionarios.setor,
                funcionarios.cargo,
                horarios.horario_inicio,
                horarios.horario_fim,
                escala_almoco.data
            FROM escala_almoco
            JOIN funcionarios ON escala_almoco.funcionario_id = funcionarios.id
            JOIN horarios ON escala_almoco.horario_id = horarios.id
            ORDER BY escala_almoco.data, horarios.horario_inicio
        """)

    escalas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "relatorio_escala.html",
        escalas=escalas,
        data_filtro=data_filtro
    )

@app.route("/calendario")
def calendario():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            funcionarios.nome,
            funcionarios.setor,
            horarios.horario_inicio,
            horarios.horario_fim,
            escala_almoco.data
        FROM escala_almoco
        JOIN funcionarios ON escala_almoco.funcionario_id = funcionarios.id
        JOIN horarios ON escala_almoco.horario_id = horarios.id
        ORDER BY escala_almoco.data, horarios.horario_inicio
    """)

    escalas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("calendario.html", escalas=escalas)
@app.route("/minha_escala")
def minha_escala():

    if "usuario" not in session:
        return redirect("/")

    email_usuario = session["usuario"]

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            funcionarios.nome,
            funcionarios.setor,
            funcionarios.cargo,
            horarios.horario_inicio,
            horarios.horario_fim,
            escala_almoco.data
        FROM escala_almoco
        JOIN funcionarios ON escala_almoco.funcionario_id = funcionarios.id
        JOIN horarios ON escala_almoco.horario_id = horarios.id
        WHERE funcionarios.email = %s
        ORDER BY escala_almoco.data, horarios.horario_inicio
    """, (email_usuario,))

    escalas = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("minha_escala.html", escalas=escalas)
@app.route("/dashboard_funcionario")
def dashboard_funcionario():

    if "usuario" not in session:
        return redirect("/")

    return render_template("dashboard_funcionario.html")

if __name__ == "__main__":
    app.run(debug=True)