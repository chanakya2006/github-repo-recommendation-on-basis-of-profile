import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Set
from webscraping import webscrape
import re
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import numpy as np

class cos :
    def main(txt1 :str, txt2 : str) -> float:
        model = SentenceTransformer('all-mpnet-base-v2')
    
        # Generate embeddings
        embedding1 = model.encode([txt1])[0]  # Get first element since encode returns a list
        embedding2 = model.encode([txt2])[0]

        # Calculate cosine similarity
        # Convert to 1 - cosine distance since cosine_distance = 1 - cosine_similarity
        similarity = 1 - cosine(embedding1, embedding2)

        return float(similarity)
class KeywordExtractor:
    
    COMMON_LANGUAGES = {
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Swift',
        'Go', 'Rust', 'TypeScript', 'Kotlin', 'R', 'MATLAB', 'Scala',
        'HTML', 'CSS', 'SQL', 'Shell', 'Perl', 'Haskell', 'Julia'
    }
    
    COMMON_TOPICS = {
        # Project Types
        "Web Development", "Mobile Apps", "Machine Learning", "Artificial Intelligence",
        "Data Science", "Big Data", "Blockchain", "Cryptocurrency", "Cybersecurity",
        "Game Development", "Automation", "Internet of Things", "IoT",
        "Embedded Systems", "Cloud Computing", "DevOps",

        # Software Development Topics
        "API Development", "REST", "GraphQL", "gRPC", "CI/CD",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Firebase",
        "Microservices", "Backend", "Frontend", "Full Stack",
        "Database", "SQL", "MySQL", "PostgreSQL", "NoSQL", "MongoDB",
        "Redis", "Cassandra", "Serverless", "Edge Computing"
    }

   
    def extract_languages(readme_text: str) -> List[str]:
        
        found_languages = set()
        for lang in KeywordExtractor.COMMON_LANGUAGES:
            pattern = r'\b' + re.escape(lang) + r'\b'
            if re.search(pattern, readme_text, re.IGNORECASE):
                # Normalize case
                found_languages.add(lang.lower())
        return list(found_languages)

    
    def extract_topics(readme_text: str) -> List[str]:
 
        found_topics = set()
        for topic in KeywordExtractor.COMMON_TOPICS:
            if re.search(r'\b' + re.escape(topic) + r'\b', readme_text, re.IGNORECASE):
                found_topics.add(topic.lower())
        return list(found_topics)
    


class GitHubRecommender:
    def __init__(self, webdriver_path: str):
        """Initialize the recommender with webdriver path"""
        self.scraper = webscrape(webdriver_path)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_recommendations_for_user(self, username: str, max_repos: int = 5, max_recommendations: int = 10):
        """Get repository recommendations for a GitHub user"""
        try:
            
            user_repos = self.scraper.get_repo_names_from_target_name(username, limit=max_repos)
            
            
            user_interests = []
            para = ""
            for repo in user_repos:
                repo_url = f"https://github.com/{repo}"
                readme_dict = self.scraper.get_repo_readme([repo_url])
                if readme_dict and repo_url in readme_dict:
                    readme_text = readme_dict[repo_url]
                    para += readme_text + "\n"
                    languages = KeywordExtractor.extract_languages(readme_text)
                    topics = KeywordExtractor.extract_topics(readme_text)
                    user_interests.extend(languages + topics)

           
            interest_counts = Counter(user_interests)
            top_interests = [item[0] for item in interest_counts.most_common(5)]

            
            recommendations = []
            for interest in top_interests:
                search_results = self.scraper.search_result_from_query(
                    interest, 
                    recommend=max_recommendations // len(top_interests),
                    max_retries=5
                )
                recommendations.extend(search_results)

            
            recommended_repos = self.scraper.get_repo_readme(recommendations)
            print(recommended_repos)
            
            cosine_values = {}
            for i in recommended_repos:
                cosine_values[i] = cos.main(para,recommended_repos[i])
            
            cosine_values = {k: v for k , v in sorted(cosine_values.items(),key=lambda item : item[1])}
            
            sorted_recommendations = {}
            for i in cosine_values:
                sorted_recommendations[i] = recommended_repos[i]
            return sorted_recommendations

        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return []
        
    

    def scrape_repository(self,repo_owner,repo_name, repo_url: str) -> Dict:


        repo_url = f'https://github.com/{repo_owner}/{repo_name}'
        
        try:
            repo_page = requests.get(repo_url, headers=self.headers)
            if repo_page.status_code != 200:
                return None

            soup = BeautifulSoup(repo_page.text, 'html.parser')
            
            
            about_section = soup.find('div', {'class': 'BorderGrid-row'})
            description = ""
            if about_section:
                desc_p = about_section.find('p', {'class': 'f4'})
                if desc_p:
                    description = desc_p.text.strip()

           
            readme_content = ""
            article = soup.find('article', {'class': 'markdown-body'})
            if article:
                readme_content = article.text.strip()

            
            languages = {}
            lang_bar = soup.find('div', {'class': 'repository-lang-stats-graph'})
            if lang_bar:
                lang_items = lang_bar.find_all('span', {'class': 'language-color'})
                for item in lang_items:
                    if item.has_attr('aria-label'):
                        lang_info = item['aria-label'].split()
                        if len(lang_info) >= 3:
                            lang_name = lang_info[0]
                            lang_percent = float(lang_info[1].replace('%', ''))
                            languages[lang_name] = lang_percent

            topics = []
            topics_div = soup.find('div', {'class': 'topic-tag-list'})
            if topics_div:
                topic_links = topics_div.find_all('a', {'class': 'topic-tag'})
                topics = [t.text.strip() for t in topic_links]

           
            url_parts = repo_url.strip('/').split('/')
            owner = url_parts[-2]
            repo_name = url_parts[-1]

            return {
                'owner': owner,
                'name': repo_name,
                'url': repo_url,
                'description': description,
                'readme_content': readme_content,
                'languages': languages,
                'topics': topics
            }

        except Exception as e:
            print(f"Error scraping repository {repo_url}: {str(e)}")
            return None

if __name__ == "__main__":
    
    recommender = GitHubRecommender("chromedriver.exe")
    recommendations = recommender.get_recommendations_for_user("chanakya2006")
    print(recommendations)
    print(json.dumps(recommendations, indent=2))