"""
from fastapi import FastAPI, HTTPException
import requests
from typing import List
from functools import lru_cache

app = FastAPI()

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

@lru_cache(maxsize=32)
def fetch_story(story_id: int):
    story_response = requests.get(HN_ITEM_URL.format(story_id))
    if story_response.status_code == 200:
        return story_response.json()
    else:
        raise HTTPException(status_code=404, detail="Story not found")

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Hacker News API! Visit /top-news?count=10 to get the top news."}

@app.get("/top-news", response_model=List[dict])
async def get_top_news(count: int = 10):
    try:
        # Fetch top stories IDs
        response = requests.get(HN_TOP_STORIES_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch top stories")

        top_stories = response.json()[:count]
        
        # Fetch each story's details
        news_items = [fetch_story(story_id) for story_id in top_stories]
        
        return news_items
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch top news")
"""


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import requests
from typing import List
from functools import lru_cache
from jinja2 import Environment, FileSystemLoader
import os

app = FastAPI()

# Setup Jinja2 environment to load templates from the current directory
template_dir = os.path.abspath(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(template_dir))

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

@lru_cache(maxsize=32)
def fetch_story(story_id: int):
    story_response = requests.get(HN_ITEM_URL.format(story_id))
    if story_response.status_code == 200:
        return story_response.json()
    else:
        raise HTTPException(status_code=404, detail="Story not found")

@app.get("/", response_class=HTMLResponse)
async def get_top_news_html(request: Request, count: int = 10):
    try:
        # Fetch top stories IDs
        response = requests.get(HN_TOP_STORIES_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch top stories")

        top_stories = response.json()[:count]
        news_items = [fetch_story(story_id) for story_id in top_stories]

        # Load and render the HTML template
        template = env.get_template('template.html')
        html_content = template.render(news_items=news_items)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch top news")
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
