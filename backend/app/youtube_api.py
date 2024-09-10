import requests
from dotenv import load_dotenv
import os
import validators
from langchain_community.document_loaders import YoutubeLoader,WebBaseLoader
from youtube_transcript_api._errors import NoTranscriptFound
from langchain.docstore.document import Document
from youtube_transcript_api import YouTubeTranscriptApi
import re



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


    def limit_word(self,transcript, word_limit=500 ):
        # Extract text with word limit
        words = []
        total_words = 0
        for entry in transcript:
            entry_words = entry.split()
            if word_limit is not None:
                if total_words + len(entry_words) > word_limit:
                    words.extend(entry_words[:word_limit - total_words])
                    break
                total_words += len(entry_words)
            words.extend(entry_words)
            if word_limit is not None and total_words >= word_limit:
                break

        full_text = " ".join(words)
        word_count = len(words)

        return full_text
    
    def get_youtube_transcript_text(self,video_url):
        try:
            video_id = self.extract_video_id(video_url)

            
            # First, try to get the manually created English transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

            transcript = [entry['text'] for entry  in transcript]

            return transcript
        except Exception as e:
            print(e)
            return  ["It seems like there is no transcript available for this video"]
        
        
        
    
    def extract_video_id(self,url):
        # Regular expression pattern to match various forms of YouTube URLs
        patterns = [
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
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

        try:
            response = requests.get(self.rapid_url, params=params ,headers=headers)
            
            if response.status_code == 200:
                search_results = response.json()

                
                subtitle_list = [i['text'] for i in search_results['content']]

                return subtitle_list
            else : 
                return  ["It seems like there is no transcript available for this video"]

        except Exception as e:
            return  [f"It seems like there is some error while transcript available for this video Error : {e.message}"]


            # complete_subtitle = " ".join(subtitle_list)
            # doc =  Document(page_content=complete_subtitle, metadata={"source": "youtube"})

            # return [doc]



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
