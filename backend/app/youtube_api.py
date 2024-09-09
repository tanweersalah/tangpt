import requests
from dotenv import load_dotenv
import os

load_dotenv()
class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API')
        self.api_url = "https://www.googleapis.com/youtube/v3/search"

    def search(self, query, max_results=1, video_type="video"):
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "type": video_type,
            "maxResults": max_results
        }
        response = requests.get(self.api_url, params=params)

        if response.status_code == 200:
            search_results = response.json()
            videos = []
            for item in search_results['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append({
                    "title": video_title,
                    "url": video_url
                })
            return videos
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None



# if __name__ == "__main__":
#     youtube = YouTubeAPI()
#     query = "Generative AI"
#     search_results = youtube.search(query, max_results=3)

#     result = {}
#     if search_results:
#         for video in search_results:
#             print(f"Video Title: {video['title']}")
#             print(f"Video URL: {video['url']}")
#             print("-----------")
