import requests
from dotenv import load_dotenv
import os
import validators
from langchain_community.document_loaders import YoutubeLoader,WebBaseLoader
from youtube_transcript_api._errors import NoTranscriptFound
from langchain.docstore.document import Document



load_dotenv()
class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API')
        self.rapid_api_key = os.getenv('RAPID_API')
        self.rapid_url = "https://youtube-transcripts.p.rapidapi.com/youtube/transcript"
        self.api_url = "https://www.googleapis.com/youtube/v3/search"

    def search(self, query, max_results=1, video_type="video",language="en"):
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "type": video_type,
            "maxResults": max_results,
            "relevanceLanguage": language
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


    def get_english_subtitle_from_url(self,video_url):

        # Initialize YoutubeLoader with the video URL
        loader = YoutubeLoader.from_youtube_url(video_url , add_video_info=True, language="en")
        
        try:
            # Try loading the manual English subtitles
            docs = loader.load()
            print("Manual English subtitles found.")
        except NoTranscriptFound:
            try:
                # Fall back to auto-generated subtitles
                docs = loader.load(generated=True)
                print("Auto-generated English subtitles found.")
            except NoTranscriptFound:

                try:
                    # Fall back to auto-translated subtitles (translated to English)
                    docs = loader.load(translation=True)
                    print("Auto-translated English subtitles found.")
                except NoTranscriptFound:
                    print("No English subtitles (manual, auto-generated, or translated) are available.")
                    return None

        return docs

    def get_subtitle_rapid_api(self, video_url):
        params = {
            
            "url": video_url
        }
        headers = {
            "x-rapidapi-key": self.rapid_api_key,
            "x-rapidapi-host": "youtube-transcripts.p.rapidapi.com"
        }
        response = requests.get(self.rapid_url, params=params ,headers=headers)
        print('rapid : ',response)
        if response.status_code == 200:
            search_results = response.json()

            print('rapid : ',search_results)
            subtitle_list = [i['text'] for i in search_results['content']]
            complete_subtitle = " ".join(subtitle_list)
            doc =  Document(page_content=complete_subtitle, metadata={"source": "youtube"})

            return [doc]



    def summarize_content(self, url):
        if validators.url(url):
            if 'youtube' in url or 'youtu.be' in url :
                try:
                    # First, try to load with manual subtitles
                    loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
                    docs = loader.load()
                    
                    # Check if subtitles were found
                    if not docs or not docs[0].page_content.strip():
                        raise ValueError("No manual subtitles found")
                    
                    return docs
                
                except Exception as e:
                    print(f"No manual subtitles found, falling back to auto-generated: {str(e)}")
                    
                    # If manual subtitles fail, try with auto-generated subtitles
                    loader = YoutubeLoader.from_youtube_url(
                        url,
                        add_video_info=True,
                        language="en",  # specify the language if needed
                        translation="en"  # specify if you want auto-translation
                    )
                    return loader.load()
            


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
