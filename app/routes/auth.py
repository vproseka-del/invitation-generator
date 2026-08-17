import os

from flask import Blueprint, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)

_PASSWORD = os.environ.get("APP_PASSWORD", "").strip()


def is_authenticated():
    return session.get("authenticated", False)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if _PASSWORD and not is_authenticated():
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if not _PASSWORD:
        return redirect(url_for("main.index"))

    error = None
    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if password == _PASSWORD:
            session["authenticated"] = True
            session.permanent = True
            next_url = request.args.get("next") or url_for("main.index")
            return redirect(next_url)
        error = "Неверный пароль."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
