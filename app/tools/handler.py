import json
from app.services.calendar import (
    check_availability,
    book_appointment,
    find_appointment,
    reschedule_appointment,
    cancel_appointment,
)
from app.config.loader import get_office_info_text


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if name == "check_availability":
            result = check_availability(
                arguments["date"],
                arguments.get("appointment_type"),
            )
            return json.dumps(result)

        elif name == "book_appointment":
            result = book_appointment(
                date_str=arguments["date"],
                time_str=arguments["time"],
                patient_name=arguments["patient_name"],
                patient_phone=arguments["patient_phone"],
                appointment_type=arguments["appointment_type"],
            )
            return json.dumps(result)

        elif name == "find_appointment":
            appointments = find_appointment(
                patient_name=arguments.get("patient_name"),
                patient_phone=arguments.get("patient_phone"),
            )
            return json.dumps({
                "found": len(appointments) > 0,
                "appointments": appointments,
            })

        elif name == "reschedule_appointment":
            result = reschedule_appointment(
                appointment_id=arguments["appointment_id"],
                new_date=arguments["new_date"],
                new_time=arguments["new_time"],
            )
            return json.dumps(result)

        elif name == "cancel_appointment":
            result = cancel_appointment(
                appointment_id=arguments["appointment_id"],
                reason=arguments.get("reason"),
            )
            return json.dumps(result)

        elif name == "get_office_info":
            topic = arguments.get("topic", "hours")
            info = get_office_info_text(topic)
            return json.dumps({"topic": topic, "info": info})

        return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})