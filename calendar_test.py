import requests
from ics import Calendar
from datetime import datetime
import zoneinfo

def get_next_class():
    url = "https://cloud.timeedit.net/nl_tue/web/stud01/ri6Y47nkyZ6ZQ1Q46d5QZ3k25121Q48Q682Z0nZQ11793w2uj46t720Z5A72D000n124l1BCAtn2l9CEA30E95212o6Q18731.ics"

    print("Fetching calendar data...")
    response = requests.get(url)

    cal = Calendar(response.text)

    amsterdam_tz  =zoneinfo.ZoneInfo("Europe/Amsterdam")
    now = datetime.now(amsterdam_tz)

    upcoming_classes = []
    for event in cal.timeline:
        if event.begin > now:
            upcoming_classes.append(event)

    if not upcoming_classes:
        return "You have nothing to do today, Boss! Fap away!"
    
    next_class = upcoming_classes[0]

    start_datetime = next_class.begin.to('Europe/Amsterdam')
    start_time = start_datetime.strftime('%H:%M')
    
    end_datetime = next_class.end.to('Europe/Amsterdam')
    end_time = end_datetime.strftime('%H:%M')

    now_date = now.date()
    class_date = start_datetime.date()

    day_diff = (class_date - now_date).days

    if day_diff == 0:
        day_str = "today"
    elif day_diff == 1:
        day_str = "tomorrow"
    else:
        day_str = f"on {start_datetime.strftime('%A')}"

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

    return f"Your next class is '{next_class.name}' on {day_str} from {start_time} to {end_time} at {final_location}, Boss! You ask like you care, but I know you won't go. What a legend!"

if __name__ == "__main__":
    result = get_next_class()
    print(result)
    

