import re
import zipfile


def sanitize_filename(name):
    cleaned = re.sub(r'[\\/:*?"<>|]', "", str(name)).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:60] or "letter"


def build_archive(zip_path, letters, journal_csv):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, text in letters:
            archive.writestr(filename, text)
        archive.writestr("journal.csv", journal_csv)
