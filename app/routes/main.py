from flask import Blueprint, jsonify, render_template, request

from app.letters.generator import generate_letter
from app.letters.projects import load_project_arguments
from app.letters.scenarios import CATEGORY_LABELS, LETTER_GOALS, SCENARIOS, resolve_category
from app.stylecheck.checker import check_text

main_bp = Blueprint("main", __name__)


def _form_context(data, errors):
    categories = [(category_id, CATEGORY_LABELS[category_id]) for category_id in SCENARIOS]
    return {
        "categories": categories,
        "goals": LETTER_GOALS,
        "fields": SCENARIOS["university"]["fields"],
        "data": data,
        "errors": errors,
    }


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/letter", methods=["GET", "POST"])
def letter():
    if request.method == "POST":
        category = request.form.get("recipient_category", "").strip()
        goal = request.form.get("letter_goal", "").strip()

        errors = {}
        data = {"recipient_category": category, "letter_goal": goal}

        if category not in SCENARIOS:
            errors["recipient_category"] = "Выберите тип организации."
        else:
            scenario = SCENARIOS[category]
            for field in scenario["fields"]:
                value = request.form.get(field, "").strip()
                data[field] = value
                if not value:
                    errors[field] = "Заполните это поле."

        if not errors:
            project_arguments = load_project_arguments(SCENARIOS[category]["project_id"])
            letter_text = generate_letter(category, data, project_arguments)
            report = check_text(letter_text)
            return render_template("letter.html", letter_text=letter_text, data=data, report=report)

        return render_template("form.html", **_form_context(data, errors))

    return render_template("form.html", **_form_context({}, {}))


@main_bp.route("/debug/resolve")
def debug_resolve():
    tests = ["Университет", "университет", "Университет / институт", "Министерство", "Партнёр", "СМИ"]
    results = {v: resolve_category(v) for v in tests}
    return jsonify(results)
