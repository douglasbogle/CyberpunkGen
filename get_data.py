import os
from dotenv import load_dotenv
import requests
import html
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from titles import searches, categories
from models import db, Video

load_dotenv()

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

BASE_URL = 'https://www.googleapis.com/youtube/v3/'

class YoutubeDataHandler:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('YOUTUBE_API_KEY')


    def search(self, query):
        ORDER = 'viewCount'
        PART = 'snippet'
        TYPE = 'video'

        Q = query

        params = {
            'part': PART,
            'order': ORDER,
            'maxResults': 100,
            'type': TYPE,
            'q': Q,
            'key': self.API_KEY,
        }

        try:
            search_result = requests.get(BASE_URL + 'search', params=params)
        except Exception as e:  # Bad Request
            print(f"Error fetching search results: {e}")
            exit(0)

        results = search_result.json()

        if ('error' in results):  # Bad Request
            print(f"API error: {results['error']}")
            exit(0)

        return results


    # Parse out titles
    def populate_db(self, info, category):
        if not isinstance(info, dict) or not info or 'items' not in info:  # Error fetching titles
            print("Error")
            exit(0)

        if 'items' not in info:  # Error fetching titles
            return KeyError

        video_dict = {}
        for item in (info['items']):
            video_title = category + item['snippet']['title']  # Classify category to improve model output
            video_id = item['id']['videoId']
            upload_time = item['snippet']['publishedAt']
            video_dict[video_id] = [video_title, video_id, upload_time]

        return video_dict


    # Function to get the videos views and tags
    def videos(self, video_dict):
        if not isinstance(video_dict, dict) or not video_dict:
            return None

        ids = [video_dict[key][1] for key in video_dict]  # Grab all video ID's to retrieve their stats and tags
        id_string = ','.join(ids)

        params_videos = {
            'part': 'snippet,statistics',
            'id': id_string,
            'key': self.API_KEY,
        }

        video_stats = requests.get(BASE_URL + 'videos' , params=params_videos)

        if video_stats.status_code != 200:  # Check for successful response
            print("Error fetching video stats")
            exit(0)

        video_info = video_stats.json()

        for item in video_info['items']:
            video_id = item['id']
            curr_views = item['statistics']['viewCount']  
            curr_tags = item['snippet'].get('tags', [])

            if video_id in video_dict:  # Ensuring this video is one of the videos we already have stored
                video_dict[video_id].append(curr_views)
                video_dict[video_id].append(', '.join(curr_tags))
            else:
                raise Exception("Something bad happened")

        return video_dict


    def save_to_db(self, video_dict):
        with app.app_context():
            for data in video_dict.values():  
                video_title, video_id, upload_time, view_count, video_tags = data
                upload_time = datetime.strptime(upload_time, '%Y-%m-%dT%H:%M:%SZ').date()

                # Check if video_id already exists
                existing_video = Video.query.filter_by(video_id=video_id).first()
                if existing_video:
                    # Update existing record
                    existing_video.title = video_title
                    existing_video.published_date = upload_time
                    existing_video.views = view_count
                    existing_video.tags = video_tags
                else:
                    # Insert new record
                    video = Video(title=video_title, video_id=video_id, published_date=upload_time, views=view_count, tags=video_tags)
                    db.session.add(video)
            db.session.commit()


    # Populate database with videos that our model will be trained on
    def get_videos(self, searches, categories):
        for title, category in zip(searches, categories):
            results = self.search(title)
            if results:
                video_dict = self.populate_db(results, category)
                if video_dict:
                    video_dict = self.videos(video_dict)
                    print(video_dict)
                    if video_dict:
                        self.save_to_db(video_dict)


if __name__ == '__main__':
    data_handler = YoutubeDataHandler()
    data_handler.get_videos(searches, categories)  # Use youtube searches and categories from titles.py

