import json


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a string.

    This currently returns placeholder responses.
    Phase 2 will connect these to real Google Calendar.
    """
    if name == "check_availability":
        return json.dumps({
            "date": arguments.get("date"),
            "available_slots": [
                {"time": "09:00", "provider": "Dr. Smith"},
                {"time": "10:30", "provider": "Dr. Smith"},
                {"time": "13:00", "provider": "Dr. Johnson"},
                {"time": "14:30", "provider": "Dr. Johnson"},
                {"time": "16:00", "provider": "Dr. Smith"},
            ]
        })

    elif name == "book_appointment":
        return json.dumps({
            "status": "confirmed",
            "appointment_id": "APT-20240601-001",
            "date": arguments.get("date"),
            "time": arguments.get("time"),
            "patient_name": arguments.get("patient_name"),
            "appointment_type": arguments.get("appointment_type"),
            "provider": "Dr. Smith",
            "message": "Appointment confirmed. Please arrive 15 minutes early."
        })

    elif name == "find_appointment":
        return json.dumps({
            "found": True,
            "appointments": [
                {
                    "appointment_id": "APT-20240601-001",
                    "date": "2025-06-05",
                    "time": "10:30",
                    "appointment_type": "cleaning",
                    "provider": "Dr. Smith",
                    "status": "confirmed"
                }
            ]
        })

    elif name == "reschedule_appointment":
        return json.dumps({
            "status": "rescheduled",
            "appointment_id": arguments.get("appointment_id"),
            "new_date": arguments.get("new_date"),
            "new_time": arguments.get("new_time"),
            "message": "Appointment rescheduled successfully."
        })

    elif name == "cancel_appointment":
        return json.dumps({
            "status": "cancelled",
            "appointment_id": arguments.get("appointment_id"),
            "message": "Appointment cancelled. Contact us if you'd like to rebook."
        })

    elif name == "get_office_info":
        info = {
            "hours": "Monday-Friday 8:00 AM - 5:00 PM, Saturday 9:00 AM - 2:00 PM, Sunday Closed",
            "location": "123 Smile Ave, Suite 100, Portland, OR 97201",
            "insurance": "We accept Delta Dental, Cigna, Aetna, MetLife, Guardian, and most PPO plans. Please call to verify your specific plan.",
            "services": "General dentistry, cleanings, fillings, crowns, root canals, whitening, extractions, emergency care, and cosmetic consultations.",
            "cancellation_policy": "Please cancel at least 24 hours in advance. Late cancellations may incur a $50 fee.",
            "emergency_policy": "For dental emergencies during office hours, call us and we will fit you in same-day. After hours, call our emergency line at (503) 555-0199.",
            "new_patient": "New patients are welcome! Your first visit includes a comprehensive exam, X-rays, and a cleaning. Please arrive 15 minutes early to complete paperwork.",
            "payment_methods": "We accept cash, credit/debit cards, HSA/FSA, and offer payment plans through CareCredit."
        }
        topic = arguments.get("topic", "hours")
        return json.dumps({"topic": topic, "info": info.get(topic, "Information not available.")})

    return json.dumps({"error": f"Unknown tool: {name}"})