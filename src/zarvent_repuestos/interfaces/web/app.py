# Web interface for the Zarvent Repuestos Flask prototype.

from flask import Flask, render_template, request

from zarvent_repuestos.modules.access.service import login


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = login(username, password)
        except Exception as e:
            message = f"Error de base de datos: {e}"
            return render_template("login.html", message=message)

        if user:
            message = f"Bienvenido, {user['username']}."
        else:
            message = "Usuario o contrasena incorrectos."

    return render_template("login.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
