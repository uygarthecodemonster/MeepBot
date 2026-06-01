import requests
from ics import Calendar
import arrow
import os
from dotenv import load_dotenv

load_dotenv()

def get_next_class():
    url = os.getenv("SCHEDULE_LINK")  # Replace with your actual .ics URL or path to the .ics file

    if not url:
        return "⚠️ SCHEDULE_LINK is not set in your .env file, Boss!"
    
    response = requests.get(url)
    response.raise_for_status()

    cal = Calendar(response.text)

    now = arrow.now('Europe/Amsterdam')

    relevant_classes = []

    for event in cal.timeline:
        if event.end > now: 
            relevant_classes.append(event)

    if not relevant_classes:
        return "You have nothing to do today, Boss! Fap away!"
    
    next_class = relevant_classes[0]

    start_datetime = next_class.begin.to('Europe/Amsterdam')
    start_time = start_datetime.strftime('%H:%M')
    
    end_datetime = next_class.end.to('Europe/Amsterdam')
    end_time = end_datetime.strftime('%H:%M')

    raw_location = next_class.location
    raw_description = next_class.description 
    
    if raw_description and "Remark:" in raw_description:
        final_location = raw_description.split("Remark:")[1].strip()
        
    elif raw_location and "Remark:" in raw_location:
        final_location = raw_location.split("Remark:")[1].strip()
        
    elif raw_location:
        final_location = raw_location.split(',')[0].strip()

    else:
        final_location = "an unspecified location"

    now_date = now.date()
    class_date = start_datetime.date()
    day_diff = (class_date - now_date).days

    is_happening_now = start_datetime <= now < end_datetime


    if is_happening_now:
        return f"🚨 Boss, you are supposed to be in '{next_class.name}' RIGHT NOW! It started at {start_time} and goes until {end_time} at {final_location}. Get your juicy ass over there!"
    else:
        if day_diff == 0:
            day_str = "today"
        elif day_diff == 1:
            day_str = "tomorrow"
        else:
            day_str = f"{start_datetime.strftime('%A')}"

        return f"Your next class is '{next_class.name}' on {day_str} from {start_time} to {end_time} at {final_location}, Boss! You ask like you care, but I know you won't go. What a legend!"

if __name__ == "__main__":
    result = get_next_class()
    print(result)
    

