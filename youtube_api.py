import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()

def get_random_youtube_video(user_mood: str):
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        return "⚠️ You forgot to put YOUTUBE_API_KEY in your .env file, Boss!"
    
    base_url = "https://www.googleapis.com/youtube/v3/"

    try:
        if user_mood.lower() == "random":
            url = base_url + "videos"
            params = {
                'part': 'id,snippet',
                'chart': 'mostPopular',
                'regionCode': 'US', # Change to 'NL' for Netherlands trending!
                'maxResults': 50,
                'key': api_key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            videos = data.get('items', [])
            if not videos:
                return "⚠️ YouTube is broken today. Go study."
            
            chosen_video = random.choice(videos)
            video_id = chosen_video['id']

        else:
            url = base_url + "search"
            params = {
                'part': 'id,snippet',
                'q': user_mood,
                'type': 'video',
                'maxResults': 5,
                'key': api_key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            videos = data.get('items', [])
            if not videos:
                return f"⚠️ No videos found for the mood '{user_mood}', Boss! Try a different mood or just ask for random!"
            
            chosen_video = random.choice(videos)
            video_id = chosen_video['id']['videoId']

        video_title = chosen_video['snippet']['title']
        channel_name = chosen_video['snippet']['channelTitle']

        video_title = video_title.replace('&quot;', '"').replace('&#39;', "'").replace('&amp;', '&')

        return f"📺 **{video_title}**\n👤 By: {channel_name}\n\nStop masturbating, Boss. Watch this instead:\nhttps://www.youtube.com/watch?v={video_id}"
    
    except Exception as e:
        return f"⚠️ Youtube API Error caused by {e}"

            


