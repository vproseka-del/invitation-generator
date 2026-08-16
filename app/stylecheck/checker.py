import json
import re
from datetime import date
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "styles" / "negative" / "rules.json"

REQUIRED_ELEMENTS = {
    "greeting": re.compile(r"Уважаем\w*", re.IGNORECASE),
    "closing": re.compile(r"С уважением", re.IGNORECASE),
}

SEVERITY_ORDER = {"error": 0, "warning": 1, "recommendation": 2}


def load_rules(path=None):
    path = path or RULES_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _apply_rule(text, rule):
    match_type = rule.get("match")
    if match_type == "substring":
        if rule["pattern"].lower() in text.lower():
            return rule["pattern"]
    elif match_type == "regex":
        flags = 0 if rule.get("case_sensitive") else re.IGNORECASE
        found = re.findall(rule["pattern"], text, flags=flags)
        if found:
            return found[0]
    elif match_type == "required_element":
        if not REQUIRED_ELEMENTS[rule["pattern"]].search(text):
            return ""
    return None


def check_text(text, rules_data=None):
    data = rules_data or load_rules()
    issues = []

    for rule in data.get("rules", []):
        if rule.get("status", "active") != "active":
            continue
        fragment = _apply_rule(text, rule)
        if fragment is not None:
            issues.append({
                "id": rule["id"],
                "severity": rule["severity"],
                "source": rule.get("source", "Negative Style"),
                "category": rule.get("category", ""),
                "fragment": fragment,
                "message": rule["message"],
                "recommendation": rule.get("recommendation", ""),
            })

    max_words = data.get("limits", {}).get("max_words")
    if max_words:
        word_count = len(text.split())
        if word_count > max_words:
            issues.append({
                "id": "NS-LIMIT",
                "severity": "warning",
                "source": "Project Arguments",
                "category": "limits",
                "fragment": f"{word_count} слов",
                "message": f"Объём письма превышает ограничение проекта ({max_words} слов)",
                "recommendation": "Сократите текст до допустимого объёма",
            })

    version = data.get("meta", {}).get("version", "")
    return _build_report(issues, version)


def _build_report(issues, version):
    issues.sort(key=lambda i: SEVERITY_ORDER[i["severity"]])
    summary = {"error": 0, "warning": 0, "recommendation": 0}
    for issue in issues:
        summary[issue["severity"]] += 1

    if summary["error"]:
        overall_status = "failed"
    elif summary["warning"]:
        overall_status = "passed_with_warnings"
    else:
        overall_status = "passed"

    return {
        "inspected_at": date.today().isoformat(),
        "rules_version": version,
        "overall_status": overall_status,
        "summary": summary,
        "issues": issues,
    }
