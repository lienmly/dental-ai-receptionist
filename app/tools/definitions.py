DENTAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check available appointment slots for a given date. Use this when a patient asks about openings or availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date to check, in YYYY-MM-DD format"
                    },
                    "appointment_type": {
                        "type": "string",
                        "description": "Type of appointment",
                        "enum": ["cleaning", "consultation", "emergency", "filling", "crown", "whitening", "extraction", "root_canal"]
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a patient. Use this after confirming the date, time, and appointment type with the patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Appointment time in HH:MM format (24-hour)"
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "patient_phone": {
                        "type": "string",
                        "description": "Patient's phone number"
                    },
                    "appointment_type": {
                        "type": "string",
                        "description": "Type of appointment",
                        "enum": ["cleaning", "consultation", "emergency", "filling", "crown", "whitening", "extraction", "root_canal"]
                    }
                },
                "required": ["date", "time", "patient_name", "patient_phone", "appointment_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_appointment",
            "description": "Look up an existing appointment by patient name or phone number. Use this when a patient wants to reschedule, cancel, or check their appointment details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "patient_phone": {
                        "type": "string",
                        "description": "Patient's phone number"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Reschedule an existing appointment to a new date and time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "The ID of the appointment to reschedule"
                    },
                    "new_date": {
                        "type": "string",
                        "description": "New appointment date in YYYY-MM-DD format"
                    },
                    "new_time": {
                        "type": "string",
                        "description": "New appointment time in HH:MM format (24-hour)"
                    }
                },
                "required": ["appointment_id", "new_date", "new_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "The ID of the appointment to cancel"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation (optional)"
                    }
                },
                "required": ["appointment_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_office_info",
            "description": "Get information about the dental office such as hours, location, accepted insurance, services offered, or policies. Use this when a patient asks general questions about the office.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to get info about",
                        "enum": ["hours", "location", "insurance", "services", "cancellation_policy", "emergency_policy", "new_patient", "payment_methods"]
                    }
                },
                "required": ["topic"]
            }
        }
    }
]