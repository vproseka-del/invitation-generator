import re

from .projects import load_project_arguments
from .scenarios import SCENARIOS


def generate_letter(scenario_id, data, project_arguments=None):
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Неизвестный сценарий: {scenario_id}")

    scenario = SCENARIOS[scenario_id]
    template_file = scenario["template_file"]
    template = template_file.read_text(encoding="utf-8")

    template_data = _build_template_data(scenario, data, project_arguments)

    text = _capitalize_you(template.format(**template_data))
    return "\n".join(line.rstrip() for line in text.splitlines())


def _build_template_data(scenario, data, project_arguments):
    template_data = dict(data)
    if not project_arguments:
        return template_data

    identity = project_arguments.get("identity", {})
    core = project_arguments.get("core_message", {})
    timing = project_arguments.get("context_and_timing", {})
    action = project_arguments.get("action", {})
    trust = project_arguments.get("trust", {})
    recipients = project_arguments.get("recipient_arguments", {})

    category = scenario.get("recipient_category")
    recipient = recipients.get(category, {}) if category else {}

    context = dict(data)
    context["project_name"] = identity.get("project_name", "")
    context["project_short_name"] = identity.get("project_short_name", "")

    template_data["project_short_name"] = identity.get("project_short_name", "")
    template_data["mission"] = recipient.get("mission") if "mission" in recipient else core.get("mission", "")
    template_data["purpose"] = recipient.get("purpose") if "purpose" in recipient else core.get("purpose", "")
    template_data["why_now_argument"] = timing.get("why_now", {}).get("argument", "")
    template_data["recipient_relevance"] = recipient.get("relevance", "").format(**context)
    template_data["recipient_benefits"] = _build_benefits(recipient, context)
    template_data["greeting"] = _build_greeting(template_data.get("recipient_name", ""))
    opener_override = (recipient.get("opener") or "").strip()
    if opener_override:
        template_data["opener"] = opener_override.format(**context)
    else:
        template_data["opener"] = _build_opener(identity, core, recipient)
    template_data["call_to_action"] = (
        recipient.get("action") or action.get("call_to_action", "")
    )
    template_data["organizational_block"] = _build_organizational_block(recipient, action)
    template_data["organizer"] = trust.get("organizer", "")
    template_data["signature_block"] = _build_signature(trust)

    survey_link = action.get("links", {}).get("survey", "")
    if survey_link:
        template_data["survey_note"] = f"Ссылка на опрос: {survey_link}"
    else:
        template_data["survey_note"] = ""

    contacts = trust.get("contacts", {})
    template_data["contact_email"] = contacts.get("email") or "<укажите адрес>"
    template_data["contact_phone"] = contacts.get("phone") or "<укажите номер>"

    return template_data


def _build_organizational_block(recipient, action):
    mode = recipient.get("survey_mode", "direct")
    if mode == "optional":
        return (action.get("optional_note") or "").strip()
    if mode == "none":
        return ""

    submission = (action.get("submission") or "").strip()
    period = (action.get("period") or action.get("deadline") or "").strip()

    parts = []

    if submission:
        parts.append(submission)

    if parts and period:
        last = parts[-1].rstrip()
        if last.endswith("."):
            last = last[:-1].rstrip()
        parts[-1] = f"{last} {period}".strip()

    sentences = []
    for part in parts:
        part = part.strip()
        if part and not part.endswith("."):
            part += "."
        sentences.append(part)

    block = " ".join(sentences)
    if not block:
        return ""
    return block


def _build_benefits(recipient, context=None):
    context = context or {}
    benefits = [
        b.strip()
        for b in recipient.get("benefits", [])
        if isinstance(b, str) and b.strip()
    ]

    paragraphs = []

    lead = (recipient.get("benefits_lead") or "").strip()
    if lead:
        paragraphs.append(lead.format(**context))

    if benefits:
        if len(benefits) == 1:
            items_text = f"{benefits[0].lower()}."
        else:
            items_text = (
                ", ".join(b.lower() for b in benefits[:-1])
                + " и "
                + benefits[-1].lower()
                + "."
            )

        intro = (recipient.get("benefits_intro") or "").strip()
        if intro:
            list_sentence = f"{intro}: {items_text}"
        elif len(benefits) == 1:
            list_sentence = f"Участие в проекте позволит вам {items_text}"
        else:
            list_sentence = f"Участие в проекте позволит вам: {items_text}"
        paragraphs.append(list_sentence)

    return "\n\n".join(paragraphs)


def _build_signature(trust):
    sig = trust.get("signatory") or {}
    name = (sig.get("name") or "").strip()
    if not name:
        return (trust.get("organizer") or "").strip()
    lines = [name]
    for key in ("position", "titles"):
        value = (sig.get(key) or "").strip()
        if value:
            lines.append(value)
    behalf = (sig.get("on_behalf_of") or "").strip()
    if behalf:
        lines.append(behalf)
    return "\n".join(lines)


_YOU_FORMS = [
    "вашими", "вашему", "вашего", "вашей", "вашем", "вашим",
    "ваши", "ваша", "ваше", "ваш", "вашу", "вами", "вам", "вас",
    "вы",
]
_WE_REGEX = re.compile(r"\b(" + "|".join(_YOU_FORMS) + r")\b", re.IGNORECASE)


def _capitalize_you(text):
    return _WE_REGEX.sub(lambda m: m.group(0).capitalize(), text)


def _build_greeting(recipient_name):
    name = (recipient_name or "").strip()
    parts = [p for p in re.split(r"\s+", name) if p]
    if not parts:
        return "Уважаемый(ая)!"

    if len(parts) >= 3:
        patronymic = parts[2]
        address = " ".join(parts[1:3])
    elif len(parts) == 2:
        patronymic = parts[1]
        address = " ".join(parts)
    else:
        patronymic = ""
        address = parts[0]

    form = "Уважаемая" if patronymic.lower().endswith("на") else "Уважаемый"
    return f"{form} {address}!"


def _build_opener(identity, core, recipient):
    ask_phrase = (recipient.get("ask_phrase") or "поддержать").strip()
    project_name = identity.get("project_name", "")
    mission_short = core.get("mission_short", "")
    if project_name and mission_short:
        return (
            f"Обращаемся к Вам с просьбой {ask_phrase} {project_name}, "
            f"направленный на {mission_short}."
        )
    project_short = identity.get("project_short_name", "")
    if project_short:
        return f"Обращаемся к вам по поручению организационного комитета проекта «{project_short}»."
    return ""
