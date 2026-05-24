import os
from datetime import datetime, timedelta
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config.settings import settings
from app.config.loader import get_appointment_duration
import json as json_module

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Build the Google Calendar service.
    
    Uses GOOGLE_SERVICE_ACCOUNT_JSON env var if available (for cloud deploy),
    otherwise falls back to the local JSON file.
    """
    if settings.google_service_account_json:
        info = json_module.loads(settings.google_service_account_json)
        credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file, scopes=SCOPES
        )
    return build("calendar", "v3", credentials=credentials)


def check_availability(date_str: str, appointment_type: Optional[str] = None) -> dict:
    """Get available slots for a given date.

    Returns a dict with available slots or an error message
    for invalid dates (past, closed days).
    """
    from app.config.loader import load_office_config, get_appointment_duration

    config = load_office_config()
    office = config["office"]

    # Parse the requested date
    try:
        requested_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        return {"error": f"Invalid date format: {date_str}. Use YYYY-MM-DD."}

    # Check if date is in the past
    from datetime import date as date_type
    if requested_date < date_type.today():
        return {"error": f"{date_str} is in the past. Please choose a future date."}

    # Check if office is closed that day
    day_name = requested_date.strftime("%A").lower()
    day_hours = office["hours"].get(day_name, "Closed")
    if day_hours == "Closed":
        return {"error": f"The office is closed on {requested_date.strftime('%A')}s. Please choose another day."}

    # Parse office hours for that day
    open_time, close_time = day_hours.replace(" ", "").split("-")
    day_start = datetime.combine(requested_date, _parse_time(open_time))
    day_end = datetime.combine(requested_date, _parse_time(close_time))

    service = get_calendar_service()

    # Get existing events for that day (use UTC)
    events_result = service.events().list(
        calendarId=settings.google_calendar_id,
        timeMin=day_start.isoformat() + "Z",
        timeMax=day_end.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    existing_events = events_result.get("items", [])

    busy_times = []
    for event in existing_events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        busy_times.append((
            datetime.fromisoformat(start.replace("Z", "")),
            datetime.fromisoformat(end.replace("Z", "")),
        ))

    slot_duration = get_appointment_duration(appointment_type) if appointment_type else 30

    available = []
    current = day_start
    while current + timedelta(minutes=slot_duration) <= day_end:
        slot_end = current + timedelta(minutes=slot_duration)
        is_free = True
        for busy_start, busy_end in busy_times:
            if current < busy_end and slot_end > busy_start:
                is_free = False
                break
        if is_free:
            available.append({
                "time": current.strftime("%H:%M"),
                "duration_minutes": slot_duration,
            })
        current += timedelta(minutes=30)

    return {"date": date_str, "available_slots": available, "total_available": len(available)}


def _parse_time(time_str: str) -> datetime.time:
    """Parse time strings like '8:00AM' or '5:00PM' into time objects."""
    time_str = time_str.strip().upper()
    for fmt in ("%I:%M%p", "%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse time: {time_str}")


def book_appointment(
    date_str: str,
    time_str: str,
    patient_name: str,
    patient_phone: str,
    appointment_type: str,
) -> dict:
    """Create a calendar event for the appointment."""
    service = get_calendar_service()

    durations = {
        "cleaning": 60,
        "consultation": 30,
        "emergency": 30,
        "filling": 60,
        "crown": 90,
        "whitening": 60,
        "extraction": 60,
        "root_canal": 120,
    }
    duration = get_appointment_duration(appointment_type)

    start_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
    end_dt = start_dt + timedelta(minutes=duration)

    event = {
        "summary": f"{appointment_type.replace('_', ' ').title()} - {patient_name}",
        "description": f"Patient: {patient_name}\nPhone: {patient_phone}\nType: {appointment_type}",
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Los_Angeles"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Los_Angeles"},
    }

    created = service.events().insert(
        calendarId=settings.google_calendar_id, body=event
    ).execute()

    return {
        "status": "confirmed",
        "appointment_id": created["id"],
        "date": date_str,
        "time": time_str,
        "patient_name": patient_name,
        "appointment_type": appointment_type,
        "duration_minutes": duration,
    }


def find_appointment(
    patient_name: Optional[str] = None, patient_phone: Optional[str] = None
) -> list:
    """Search for appointments by patient name or phone."""
    service = get_calendar_service()

    # Search upcoming events (next 30 days)
    now = datetime.utcnow()
    time_max = now + timedelta(days=30)

    events_result = service.events().list(
        calendarId=settings.google_calendar_id,
        timeMin=now.isoformat() + "Z",
        timeMax=time_max.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
        q=patient_name or patient_phone or "",
    ).execute()
    events = events_result.get("items", [])

    results = []
    for event in events:
        description = event.get("description", "")
        # Match by name or phone in description
        search_term = (patient_name or patient_phone or "").lower()
        if search_term and search_term not in description.lower() and search_term not in event.get("summary", "").lower():
            continue

        start = event["start"].get("dateTime", event["start"].get("date"))
        start_dt = datetime.fromisoformat(start.replace("Z", ""))

        results.append({
            "appointment_id": event["id"],
            "date": start_dt.strftime("%Y-%m-%d"),
            "time": start_dt.strftime("%H:%M"),
            "summary": event.get("summary", ""),
            "status": "confirmed",
        })

    return results


def reschedule_appointment(appointment_id: str, new_date: str, new_time: str) -> dict:
    """Move an existing appointment to a new date/time."""
    service = get_calendar_service()

    # Get the existing event to preserve its duration
    event = service.events().get(
        calendarId=settings.google_calendar_id, eventId=appointment_id
    ).execute()

    old_start = datetime.fromisoformat(event["start"]["dateTime"])
    old_end = datetime.fromisoformat(event["end"]["dateTime"])
    duration = old_end - old_start

    new_start = datetime.fromisoformat(f"{new_date}T{new_time}:00")
    new_end = new_start + duration

    event["start"] = {"dateTime": new_start.isoformat(), "timeZone": "America/Los_Angeles"}
    event["end"] = {"dateTime": new_end.isoformat(), "timeZone": "America/Los_Angeles"}

    updated = service.events().update(
        calendarId=settings.google_calendar_id, eventId=appointment_id, body=event
    ).execute()

    return {
        "status": "rescheduled",
        "appointment_id": updated["id"],
        "new_date": new_date,
        "new_time": new_time,
    }


def cancel_appointment(appointment_id: str, reason: Optional[str] = None) -> dict:
    """Delete an appointment from the calendar."""
    service = get_calendar_service()

    service.events().delete(
        calendarId=settings.google_calendar_id, eventId=appointment_id
    ).execute()

    return {
        "status": "cancelled",
        "appointment_id": appointment_id,
        "reason": reason,
    }