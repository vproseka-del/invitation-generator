import csv
import io

HEADERS = ["№", "Организация", "Статус", "Имя файла", "Ошибка"]


def build_journal(rows_info):
    entries = []
    for info in rows_info:
        entries.append({
            "number": info["row"],
            "organization": info.get("organization", ""),
            "status": info["status"],
            "filename": info.get("filename", ""),
            "error": info.get("error", ""),
        })
    return entries


def journal_to_csv(entries):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(HEADERS)
    for entry in entries:
        writer.writerow([
            entry["number"],
            entry["organization"],
            entry["status"],
            entry["filename"],
            entry["error"],
        ])
    return "\ufeff" + buffer.getvalue()
