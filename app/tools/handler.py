import json
from app.services.calendar import (
    check_availability,
    book_appointment,
    find_appointment,
    reschedule_appointment,
    cancel_appointment,
)


# Office info stays hardcoded (this becomes the config file in Phase 3)
OFFICE_INFO = {
    "hours": "Monday-Friday 8:00 AM - 5:00 PM, Saturday 9:00 AM - 2:00 PM, Sunday Closed",
    "location": "123 Smile Ave, Suite 100, Portland, OR 97201",
    "insurance": "We accept Delta Dental, Cigna, Aetna, MetLife, Guardian, and most PPO plans. Please call to verify your specific plan.",
    "services": "General dentistry, cleanings, fillings, crowns, root canals, whitening, extractions, emergency care, and cosmetic consultations.",
    "cancellation_policy": "Please cancel at least 24 hours in advance. Late cancellations may incur a $50 fee.",
    "emergency_policy": "For dental emergencies during office hours, call us and we will fit you in same-day. After hours, call our emergency line at (503) 555-0199.",
    "new_patient": "New patients are welcome! Your first visit includes a comprehensive exam, X-rays, and a cleaning. Please arrive 15 minutes early to complete paperwork.",
    "payment_methods": "We accept cash, credit/debit cards, HSA/FSA, and offer payment plans through CareCredit.",
}


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if name == "check_availability":
            slots = check_availability(
                arguments["date"],
                arguments.get("appointment_type"),
            )
            return json.dumps({
                "date": arguments["date"],
                "available_slots": slots,
                "total_available": len(slots),
            })

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
            return json.dumps({
                "topic": topic,
                "info": OFFICE_INFO.get(topic, "Information not available."),
            })

        return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})