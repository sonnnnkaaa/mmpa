import os
import re
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize

load_dotenv()
CORE_API_KEY = os.getenv("CORE_API_KEY")
URL = "https://api.core.ac.uk/v3/search/works"

def search_works(api_key: str, limit: int = 300, offset: int = 0):
    headers = {"Authorization": f"Bearer {api_key}"}
    query = f"documentType:\"journal article\" AND fieldOfStudy:medicine AND yearPublished>=2010"
    params = {"q": query,
              "limit": limit,
              "offset": offset}
    try:
        response = requests.get(URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def clean_text(text: str):
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\b10\.\d{4,9}/\S+', '', text)
    text = re.sub(r'\bPage \d+ of \d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s.,;:!?()\[\]%\-–—]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


data = search_works(api_key=CORE_API_KEY)
if data:
    with open("data/articles_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=3)

with open("data/articles_response.json") as json_file:
    json_data = json.load(json_file)["results"]
    json_file.close()

articles = {}
for res in json_data:
    if res["fullText"] and res["language"]:
        if res["language"]["code"] == "en":
            words = word_tokenize(res["fullText"])
            articles[res["id"]] = [len(words), res["title"], res["yearPublished"], res["fullText"]]
sorted_articles = dict(sorted(articles.items(), key=lambda item: item[1][0]))

ids = list(sorted_articles.keys())[:30]
words_cnt = [val[0] for val in list(sorted_articles.values())[:30]]
titles = [val[1] for val in list(sorted_articles.values())[:30]]
years = [val[2] for val in list(sorted_articles.values())[:30]]
texts = [clean_text(val[3]) for val in list(sorted_articles.values())[:30]]

df = pd.DataFrame({
    "id": ids,
    "words_cnt": words_cnt,
    "title": titles,
    "year": years,
    "text": texts
})

df.to_json(
    "data/articles.jsonl",
    orient="records",
    lines=True,
    force_ascii=False,
    indent=None
)

print(df.info())
print(df.head())