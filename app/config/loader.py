import os
import yaml

_config = None


def load_office_config(path: str = None) -> dict:
    global _config
    if _config is not None:
        return _config

    if path is None:
        path = os.path.join(os.path.dirname(__file__), "office.yaml")

    with open(path, "r") as f:
        _config = yaml.safe_load(f)

    return _config


def get_office_info_text(topic: str) -> str:
    """Get formatted office info for a given topic."""
    config = load_office_config()
    office = config["office"]

    if topic == "hours":
        hours_lines = [f"  {day.title()}: {time}" for day, time in office["hours"].items()]
        return "Office Hours:\n" + "\n".join(hours_lines)

    elif topic == "location":
        loc = office["location"]
        return f"{office['name']}\n{loc['address']}\n{loc['city']}, {loc['state']} {loc['zip']}\nPhone: {office['phone']}"

    elif topic == "insurance":
        ins = config["insurance"]
        providers = ", ".join(ins["accepted"])
        return f"Accepted insurance: {providers}. {ins['note']}"

    elif topic == "services":
        types = config["appointment_types"]
        services = [f"  - {info['display_name']} ({info['duration_minutes']} min)" for info in types.values()]
        return "Services offered:\n" + "\n".join(services)

    elif topic in ("cancellation_policy", "emergency_policy", "new_patient", "payment_methods"):
        # Map topic names to policy keys
        key = topic.replace("_policy", "")
        return config["policies"].get(key, "Information not available.")

    return "Information not available."


def get_appointment_duration(appointment_type: str) -> int:
    """Get duration in minutes for an appointment type."""
    config = load_office_config()
    types = config["appointment_types"]
    if appointment_type in types:
        return types[appointment_type]["duration_minutes"]
    return 30


def build_system_prompt(today: str) -> str:
    """Build the system prompt dynamically from office config."""
    config = load_office_config()
    office = config["office"]
    loc = office["location"]

    hours_lines = [f"  {day.title()}: {time}" for day, time in office["hours"].items()]
    hours_text = "\n".join(hours_lines)

    services = []
    for key, info in config["appointment_types"].items():
        providers = ", ".join(info.get("providers", []))
        services.append(f"  - {info['display_name']} ({info['duration_minutes']} min) — providers: {providers}")
    services_text = "\n".join(services)

    insurance_list = ", ".join(config["insurance"]["accepted"])

    return f"""You are a friendly receptionist at {office['name']}. Today's date is {today}.

Office Details:
  Address: {loc['address']}, {loc['city']}, {loc['state']} {loc['zip']}
  Phone: {office['phone']}

Office Hours:
{hours_text}

Services:
{services_text}

Accepted Insurance: {insurance_list}. {config['insurance']['note']}

Policies:
  Cancellation: {config['policies']['cancellation']}
  Emergency: {config['policies']['emergency']}
  New Patients: {config['policies']['new_patient']}
  Payment: {config['policies']['payment_methods']}

IMPORTANT RULES:
- Always use the provided tools to check real availability and book appointments. Never make up times or availability.
- When a patient wants to book, collect: appointment type, preferred date/time, full name, and phone number. You can collect these naturally across multiple messages.
- If a tool returns an error (like the office is closed that day), relay that information helpfully and suggest alternatives.
- If a patient asks about something outside your scope (complex medical questions, specific treatment plans, billing disputes), say: "That's a great question — let me have our team get back to you. Can I take your name and number?"
- Keep responses concise. No walls of text.
- Do not use markdown tables. Use simple, natural formatting."""