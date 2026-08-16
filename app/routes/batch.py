import os
import shutil
import tempfile
import uuid

from flask import (
    Blueprint,
    abort,
    after_this_request,
    render_template,
    request,
    send_file,
    url_for,
)

from app.batch.journal import build_journal, journal_to_csv
from app.batch.packager import build_archive, sanitize_filename
from app.batch.reader import read_xlsx
from app.letters.generator import generate_letter
from app.letters.projects import load_project_arguments
from app.letters.scenarios import SCENARIOS, resolve_category

batch_bp = Blueprint("batch", __name__)

BATCH_DIR = os.path.join(tempfile.gettempdir(), "invitationgenerator_batch")

BASE_FIELDS = {label: key for key, label in SCENARIOS["university"]["fields"].items()}
REQUIRED_COLUMNS = dict(BASE_FIELDS)
REQUIRED_COLUMNS["Тип организации"] = "recipient_category"
OPTIONAL_COLUMNS = {"Цель письма": "letter_goal"}


@batch_bp.route("/batch", methods=["GET", "POST"])
def batch():
    if request.method == "GET":
        return render_template("batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS), error=None)

    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="Выберите файл Excel (.xlsx).",
        )
    if not uploaded.filename.lower().endswith(".xlsx"):
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="Поддерживается только формат Excel (.xlsx).",
        )

    try:
        missing, records = read_xlsx(uploaded.stream, REQUIRED_COLUMNS, OPTIONAL_COLUMNS)
    except Exception:
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="Не удалось прочитать файл. Убедитесь, что это корректный файл Excel (.xlsx) с данными на первом листе.",
        )

    if missing:
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="В таблице отсутствуют обязательные столбцы: " + ", ".join(missing) + ".",
        )

    if not records:
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="В таблице нет строк с данными.",
        )

    try:
        project_arguments = load_project_arguments("fiziki_i_liriki")
    except Exception:
        return render_template(
            "batch_upload.html", required_columns=list(REQUIRED_COLUMNS), optional_columns=list(OPTIONAL_COLUMNS),
            error="Не удалось загрузить данные проекта. Повторите попытку позже.",
        )

    letters = {}
    rows_info = []
    for record in records:
        data = record["data"]
        row = record["row"]
        organization = data.get("organization", "")
        category = resolve_category(data.get("recipient_category", ""))

        if record["missing"]:
            rows_info.append({
                "row": row,
                "organization": organization,
                "status": "ошибка",
                "filename": "",
                "error": ", ".join(record["missing"]),
            })
            continue

        if category is None:
            rows_info.append({
                "row": row,
                "organization": organization,
                "status": "ошибка",
                "filename": "",
                "error": f"Неизвестный тип организации: {data['recipient_category']}",
            })
            continue

        try:
            text = generate_letter(category, data, project_arguments)
        except Exception as exc:
            rows_info.append({
                "row": row,
                "organization": organization,
                "status": "ошибка",
                "filename": "",
                "error": f"ошибка генерации: {exc}",
            })
            continue

        filename = f"{sanitize_filename(organization)}_{row}.txt"
        letters[filename] = text
        rows_info.append({
            "row": row,
            "organization": organization,
            "status": "готово",
            "filename": filename,
            "error": "",
        })

    journal = build_journal(rows_info)
    csv_text = journal_to_csv(journal)

    token = uuid.uuid4().hex
    target_dir = os.path.join(BATCH_DIR, token)
    os.makedirs(target_dir, exist_ok=True)
    zip_path = os.path.join(target_dir, "letters.zip")
    build_archive(zip_path, list(letters.items()), csv_text)

    return render_template(
        "batch_result.html",
        total=len(rows_info),
        letters_count=len(letters),
        errors_count=len(rows_info) - len(letters),
        journal=journal,
        download_url=url_for("batch.download", token=token),
    )


@batch_bp.route("/batch/download/<token>")
def download(token):
    target_dir = os.path.join(BATCH_DIR, token)
    zip_path = os.path.join(target_dir, "letters.zip")

    if not os.path.isfile(zip_path):
        abort(404)

    @after_this_request
    def cleanup(response):
        try:
            shutil.rmtree(target_dir)
        except OSError:
            pass
        return response

    return send_file(zip_path, as_attachment=True, download_name="letters.zip")
