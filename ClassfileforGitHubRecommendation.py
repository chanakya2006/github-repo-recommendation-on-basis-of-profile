import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter

class GitHubProjectRecommender:
    def __init__(self, db_file="repository_database.json"):
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Store scraped repositories in memory
        self.stored_repositories = []
        self.user_profiles = {}
        
        # Database file path
        self.db_file = db_file
        
        # Load existing database if it exists
        self.load_database()

    def load_database(self):
        """Load repositories database from JSON file if it exists"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stored_repositories = data.get('repositories', [])
                    self.user_profiles = data.get('user_profiles', {})
                print(f"Loaded {len(self.stored_repositories)} repositories and {len(self.user_profiles)} user profiles from database")
            except Exception as e:
                print(f"Error loading database: {e}")
                # Initialize empty database if loading fails
                self.stored_repositories = []
                self.user_profiles = {}
        
    def save_database(self):
        """Save repositories and user profiles to JSON database"""
        try:
            data = {
                'repositories': self.stored_repositories,
                'user_profiles': self.user_profiles
            }
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Database saved with {len(self.stored_repositories)} repositories and {len(self.user_profiles)} user profiles")
        except Exception as e:
            print(f"Error saving database: {e}")
        
    def extract_languages_from_readme(self, readme_text):
        """Extract programming languages from README content"""
        # Common programming languages to look for
        common_languages = {
            'Python','python', 'JavaScript','javascript', 'Java','java', 'C++','c++', 'C#','c#', 'Ruby','ruby', 'PHP','php', 'Swift','swift',
            'Go','GO','go', 'Rust','rust', 'TypeScript','typescript','Typescript', 'Kotlin','kotlin', 'R', 'MATLAB','matlab', 'Scala', 'sacala',
            'HTML', 'CSS', 'SQL', 'Shell', 'Perl', 'Haskell', 'Julia'
        }
        
        # Find languages in text
        found_languages = set()
        for lang in common_languages:
            # Look for language mentions with word boundaries
            pattern = r'\b' + re.escape(lang) + r'\b'
            if re.search(pattern, readme_text, re.IGNORECASE):
                found_languages.add(lang)
                
        return list(found_languages)

    def extract_topics_from_readme(self, readme_text):
        """Extract potential topics/interests from README content"""
        common_topics = {
            # Programming Languages
    "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "Go", "Rust",
    "PHP", "Swift", "Kotlin", "Ruby", "Dart", "R", "Shell", "Perl", "Lua",
    "Scala", "Haskell",

    # Project Types
    "Web Development", "Mobile Apps", "Machine Learning", "Artificial Intelligence",
    "Data Science", "Big Data", "Blockchain", "Cryptocurrency", "Cybersecurity",
    "Game Development", "Automation & Scripting", "Internet of Things (IoT)",
    "Embedded Systems", "Cloud Computing", "DevOps",

    # Software Development Topics
    "API Development", "RESTful APIs", "GraphQL", "gRPC", "DevOps", "CI/CD Pipelines",
    "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud Platform (GCP)", "Firebase",
    "Microservices Architecture", "Backend Development", "Frontend Development",
    "Full Stack Development", "Database Management", "SQL", "MySQL", "PostgreSQL",
    "NoSQL", "MongoDB", "Redis", "Cassandra", "Serverless Computing", "Edge Computing"
        }
        
        found_topics = set()
        for topic in common_topics:
            if re.search(r'\b' + re.escape(topic) + r'\b', readme_text, re.IGNORECASE):
                found_topics.add(topic)
                
        return list(found_topics)

    def scrape_repository(self, repo_owner, repo_name):
        """Scrape detailed information about a GitHub repository"""
        # Check if repository already exists in database
        for repo in self.stored_repositories:
            if repo.get('owner') == repo_owner and repo.get('name') == repo_name:
                print(f"Using cached data for repository {repo_owner}/{repo_name}")
                return repo
                
        repo_url = f'https://github.com/{repo_owner}/{repo_name}'
        
        try:
            # Get repository page
            repo_page = requests.get(repo_url, headers=self.headers)
            if repo_page.status_code != 200:
                print(f"Failed to access repository: {repo_url}")
                return None
                
            repo_soup = BeautifulSoup(repo_page.text, 'html.parser')
            
            # Extract basic repository info
            about_section = repo_soup.find('div', {'class': 'BorderGrid-row'})
            description = ""
            if about_section:
                desc_p = about_section.find('p', {'class': 'f4'})
                if desc_p:
                    description = desc_p.text.strip()
            
            # Extract README content
            readme_content = ""
            article = repo_soup.find('article', {'class': 'markdown-body'})
            if article:
                readme_content = article.text.strip()
            
            # Extract languages
            languages = {}
            lang_bar = repo_soup.find('div', {'class': 'repository-lang-stats-graph'})
            if lang_bar:
                lang_items = lang_bar.find_all('span', {'class': 'language-color'})
                for item in lang_items:
                    if item.has_attr('aria-label'):
                        lang_info = item['aria-label'].split()
                        if len(lang_info) >= 3:
                            lang_name = lang_info[0]
                            lang_percent = float(lang_info[1].replace('%', ''))
                            languages[lang_name] = lang_percent
            
            # If languages not found through language bar, try extracting from README
            if not languages:
                langs_from_readme = self.extract_languages_from_readme(readme_content)
                for lang in langs_from_readme:
                    languages[lang] = 1  # Placeholder percentage
            
            # Extract topics/tags
            topics = []
            topics_div = repo_soup.find('div', {'class': 'topic-tag-list'})
            if topics_div:
                topic_links = topics_div.find_all('a', {'class': 'topic-tag'})
                topics = [t.text.strip() for t in topic_links]
            
            # If no topics found, extract potential topics from README
            if not topics:
                topics = self.extract_topics_from_readme(readme_content)
            
            # Extract stars/forks for popularity
            stars = 0
            forks = 0
            
            social_count = repo_soup.find_all('a', {'class': 'social-count'})
            if len(social_count) >= 2:
                try:
                    stars = int(social_count[0].text.strip().replace(',', ''))
                    forks = int(social_count[1].text.strip().replace(',', ''))
                except (ValueError, IndexError):
                    pass
            
            repository_data = {
                'owner': repo_owner,
                'name': repo_name,
                'url': repo_url,
                'description': description,
                'readme_content': readme_content,
                'languages': languages,
                'topics': topics,
                'stars': stars,
                'forks': forks,
                'last_updated': self._get_current_timestamp()
            }
            
            # Add to stored repositories
            self.stored_repositories.append(repository_data)
            # Save updated database
            self.save_database()
            
            return repository_data
            
        except Exception as e:
            print(f"Error scraping repository {repo_owner}/{repo_name}: {e}")
            return None

    def _get_current_timestamp(self):
        """Get current timestamp for database entries"""
        from datetime import datetime
        return datetime.now().isoformat()

    def scrape_user_profile(self, username):
        """Scrape GitHub user profile and their repositories"""
        # Check if user profile already exists in database
        if username in self.user_profiles:
            print(f"Using cached profile for user {username}")
            return self.user_profiles[username]
            
        profile_url = f'https://github.com/{username}'
        repos_url = f'https://github.com/{username}?tab=repositories'
        
        try:
            # Get profile page
            profile_page = requests.get(profile_url, headers=self.headers)
            if profile_page.status_code != 200:
                print(f"Failed to access profile: {profile_url}")
                return None
                
            profile_soup = BeautifulSoup(profile_page.text, 'html.parser')
            
            # Extract basic profile info
            bio_div = profile_soup.find('div', {'class': 'p-note'})
            bio = bio_div.text.strip() if bio_div else ""
            
            # Check for README profile
            readme_content = ""
            readme_url = f'https://github.com/{username}/{username}'
            readme_page = requests.get(readme_url, headers=self.headers)
            if readme_page.status_code == 200:
                readme_soup = BeautifulSoup(readme_page.text, 'html.parser')
                article = readme_soup.find('article', {'class': 'markdown-body'})
                if article:
                    readme_content = article.text.strip()
            
            # Get repositories page
            repos_page = requests.get(repos_url, headers=self.headers)
            repos_soup = BeautifulSoup(repos_page.text, 'html.parser')
            
            # Extract repositories
            repos = []
            repo_list = repos_soup.find_all('li', {'class': 'source'})
            if not repo_list:  # Try alternative class if not found
                repo_list = repos_soup.find_all('li', {'class': 'col-12'})
            
            # If still no repos found, try a different approach
            if not repo_list:
                repo_items = repos_soup.find_all('div', {'class': 'wb-break-word'})
                for item in repo_items:
                    repo_link = item.find('a')
                    if repo_link and '/' in repo_link.text:
                        repo_parts = repo_link.text.strip().split('/')
                        if len(repo_parts) == 2 and repo_parts[0] == username:
                            repo_name = repo_parts[1]
                            repos.append({
                                'name': repo_name,
                                'owner': username,
                                'url': f'https://github.com/{username}/{repo_name}'
                            })
            else:
                for repo in repo_list[:10]:
                    name_elem = repo.find('a', {'itemprop': 'name codeRepository'})
                    if not name_elem:
                        name_elem = repo.find('a', {'class': 'mr-2'})
                    
                    if not name_elem:
                        continue
                        
                    desc_elem = repo.find('p', {'class': 'pinned-item-desc'}) or repo.find('p', {'class': 'mb-0'})
                    lang_elem = repo.find('span', {'itemprop': 'programmingLanguage'}) or repo.find('span', {'class': 'ml-0'})
                    
                    name = name_elem.text.strip()
                    description = desc_elem.text.strip() if desc_elem else ""
                    language = lang_elem.text.strip() if lang_elem else ""
                    
                    repos.append({
                        'name': name,
                        'owner': username,
                        'url': f'https://github.com/{username}/{name}',
                        'description': description,
                        'language': language
                    })
            
            # Scrape detailed info for each repository
            detailed_repos = []
            for repo in repos[:10]:  # Limit to first 10 repos to avoid rate limiting
                detailed_repo = self.scrape_repository(username, repo['name'])
                if detailed_repo:
                    detailed_repos.append(detailed_repo)
            
            # Extract languages from repos and README
            languages_from_readme = self.extract_languages_from_readme(readme_content)
            languages_from_repos = []
            for repo in detailed_repos:
                languages_from_repos.extend(list(repo['languages'].keys()))
            
            # Count language occurrences
            all_languages = languages_from_readme + languages_from_repos
            language_counter = Counter(all_languages)
            
            # Extract topics from repos and README
            topics_from_readme = self.extract_topics_from_readme(readme_content)
            topics_from_repos = []
            for repo in detailed_repos:
                topics_from_repos.extend(repo['topics'])
            
            # Count topic occurrences
            all_topics = topics_from_readme + topics_from_repos
            topic_counter = Counter(all_topics)
            
            # Create user profile
            user_profile = {
                'username': username,
                'bio': bio,
                'readme_content': readme_content,
                'repositories': [repo['name'] for repo in detailed_repos],  # Store just repo names to avoid duplication
                'top_languages': dict(language_counter.most_common(10)),
                'top_topics': dict(topic_counter.most_common(10)),
                'last_updated': self._get_current_timestamp()
            }
            
            # Cache user profile
            self.user_profiles[username] = user_profile
            
            # Save updated database
            self.save_database()
            
            return user_profile
            
        except Exception as e:
            print(f"Error scraping profile for {username}: {e}")
            return None

    def create_project_embedding(self, repo_data):
        """Create text embedding for a repository"""
        project_text = f"""
        Repository: {repo_data['name']}
        Owner: {repo_data['owner']}
        Description: {repo_data['description']}
        Languages: {', '.join(repo_data['languages'].keys())}
        Topics: {', '.join(repo_data['topics'])}
        README Content: {repo_data.get('readme_content', '')}
        """
        return self.model.encode([project_text])[0]

    def create_user_preference_embedding(self, user_profile):
        """Create embedding representing user's preferences based on their profile"""
        # Combine bio, readme, top languages and topics
        preference_text = f"""
        Bio: {user_profile['bio']}
        Top Languages: {', '.join(user_profile['top_languages'].keys())}
        Top Topics: {', '.join(user_profile['top_topics'].keys())}
        README Content: {user_profile['readme_content']}
        """
        return self.model.encode([preference_text])[0]

    def get_recommendations_from_database(self, user_profile, max_recommendations=5):
        """
        Get project recommendations for a user from the stored database
        
        Parameters:
        user_profile (dict): User profile data
        max_recommendations (int): Maximum number of recommendations to return
        
        Returns:
        list: Recommended repositories from database
        """
        if not self.stored_repositories:
            return []
            
        # Skip user's own repositories
        username = user_profile['username']
        candidate_repos = [repo for repo in self.stored_repositories 
                          if repo['owner'] != username]
        
        if not candidate_repos:
            return []
        
        # Get embedding for user preferences
        user_embedding = self.create_user_preference_embedding(user_profile)
        
        # Create embeddings for candidate repositories
        repo_embeddings = np.array([
            self.create_project_embedding(repo) for repo in candidate_repos
        ])
        
        # Calculate similarities
        similarities = cosine_similarity([user_embedding], repo_embeddings)[0]
        
        # Get top similar repositories
        top_indices = np.argsort(similarities)[-max_recommendations:][::-1]
        
        # Create recommendation objects
        recommendations = []
        for idx, similarity in zip(top_indices, similarities[top_indices]):
            repo = candidate_repos[idx]
            recommendations.append({
                'owner': repo['owner'],
                'name': repo['name'],
                'description': repo['description'],
                'url': repo['url'],
                'languages': list(repo['languages'].keys()),
                'topics': repo['topics'],
                'similarity_score': float(similarity),
                'stars': repo.get('stars', 0),
                'forks': repo.get('forks', 0),
                'from_database': True
            })
        
        return recommendations

    def scrape_trending_repositories(self, language=None):
        """Scrape trending repositories for additional recommendations"""
        trending_url = 'https://github.com/trending'
        if language:
            trending_url += f'/{language}'
        
        try:
            trending_page = requests.get(trending_url, headers=self.headers)
            trending_soup = BeautifulSoup(trending_page.text, 'html.parser')
            
            trending_repos = []
            repo_articles = trending_soup.find_all('article', {'class': 'Box-row'})
            
            for article in repo_articles[:10]:
                repo_link = article.find('h2').find('a')
                if not repo_link:
                    continue
                
                repo_path = repo_link['href'].strip('/')
                if '/' in repo_path:
                    owner, name = repo_path.split('/')
                    
                    description_p = article.find('p')
                    description = description_p.text.strip() if description_p else ""
                    
                    language_span = article.find('span', {'itemprop': 'programmingLanguage'})
                    language = language_span.text.strip() if language_span else ""
                    
                    trending_repos.append({
                        'owner': owner,
                        'name': name,
                        'description': description,
                        'language': language,
                        'url': f'https://github.com/{repo_path}'
                    })
            
            return trending_repos
            
        except Exception as e:
            print(f"Error scraping trending repositories: {e}")
            return []

    def search_repositories(self, query, language=None):
        """Search for repositories based on query"""
        search_url = f'https://github.com/search?q={query}'
        if language:
            search_url += f'+language:{language}'
        search_url += '&type=repositories'
        
        try:
            search_page = requests.get(search_url, headers=self.headers)
            search_soup = BeautifulSoup(search_page.text, 'html.parser')
            
            search_results = []
            result_items = search_soup.find_all('li', {'class': 'repo-list-item'})
            
            # If the repo-list-item class isn't found, try another selector
            if not result_items:
                result_items = search_soup.select('div.Box-row')
            
            for item in result_items[:10]:
                # Try different selectors to find repository links
                repo_link = None
                if item.find('a', {'class': 'v-align-middle'}):
                    repo_link = item.find('a', {'class': 'v-align-middle'})
                elif item.find('a', {'data-hydro-click-hmac'}):
                    links = item.find_all('a')
                    for link in links:
                        if '/' in link.text and 'github.com' not in link.text:
                            repo_link = link
                            break
                
                if not repo_link or not repo_link.has_attr('href'):
                    continue
                
                repo_path = repo_link['href'].strip('/')
                if '/' in repo_path:
                    owner, name = repo_path.split('/')
                    
                    # Try different selectors for description
                    description_p = item.find('p', {'class': 'mb-1'}) or item.find('p', {'class': 'col-9'})
                    description = description_p.text.strip() if description_p else ""
                    
                    search_results.append({
                        'owner': owner,
                        'name': name,
                        'description': description,
                        'url': f'https://github.com/{repo_path}'
                    })
            
            return search_results
            
        except Exception as e:
            print(f"Error searching repositories: {e}")
            return []   
    
    def get_recommendations_for_topic(self, topic, language=None, max_recommendations=10):
        """
        Get project recommendations related to a specific topic or language
        
        Parameters:
        topic (str): Topic or keyword to search for
        language (str, optional): Programming language to filter by
        max_recommendations (int): Maximum number of recommendations to return
        
        Returns:
        list: Recommended repositories
        """
        # Search for repositories on GitHub
        search_results = self.search_repositories(topic, language)
        candidate_repos = []
        
        # Get detailed repository data
        for repo in search_results:
            detailed_repo = self.scrape_repository(repo['owner'], repo['name'])
            if detailed_repo:
                candidate_repos.append(detailed_repo)
        
        # If not enough from search, include trending repositories
        if len(candidate_repos) < max_recommendations and language:
            trending_repos = self.scrape_trending_repositories(language)
            for repo in trending_repos:
                detailed_repo = self.scrape_repository(repo['owner'], repo['name'])
                if detailed_repo and detailed_repo not in candidate_repos:
                    candidate_repos.append(detailed_repo)
        
        # If still not enough, add from database that match the topic/language
        if len(candidate_repos) < max_recommendations:
            for repo in self.stored_repositories:
                # Check if repo matches topic
                topic_match = (
                    topic.lower() in repo['name'].lower() or
                    topic.lower() in repo['description'].lower() or
                    any(topic.lower() in t.lower() for t in repo['topics'])
                )
                
                # Check if repo matches language (if specified)
                lang_match = True
                if language:
                    lang_match = any(language.lower() == lang.lower() for lang in repo['languages'])
                
                if topic_match and lang_match and repo not in candidate_repos:
                    candidate_repos.append(repo)
                    if len(candidate_repos) >= max_recommendations * 2:
                        break
        
        # If no candidates found, return empty list
        if not candidate_repos:
            return []
        
        # Create topic embedding
        topic_text = f"Topic: {topic}"
        if language:
            topic_text += f"\nLanguage: {language}"
        topic_embedding = self.model.encode([topic_text])[0]
        
        # Create embeddings for candidate repositories
        repo_embeddings = np.array([
            self.create_project_embedding(repo) for repo in candidate_repos
        ])
        
        # Calculate similarities
        similarities = cosine_similarity([topic_embedding], repo_embeddings)[0]
        
        # Get top similar repositories
        top_indices = np.argsort(similarities)[-max_recommendations:][::-1]
        
        # Create recommendation objects
        recommendations = []
        for idx, similarity in zip(top_indices, similarities[top_indices]):
            repo = candidate_repos[idx]
            recommendations.append({
                'owner': repo['owner'],
                'name': repo['name'],
                'description': repo['description'],
                'url': repo['url'],
                'languages': list(repo['languages'].keys()),
                'topics': repo['topics'],
                'similarity_score': float(similarity),
                'stars': repo.get('stars', 0),
                'forks': repo.get('forks', 0)
            })
        
        return recommendations
            
    def get_recommendations_for_user(self, username, max_recommendations=10, web_search_ratio=0.5):
        """
        Get project recommendations for a user based on their profile and repositories,
        with a specified ratio coming from database vs web search
        
        Parameters:
        username (str): GitHub username
        max_recommendations (int): Total number of recommendations to return
        web_search_ratio (float): Ratio of recommendations to get from web search (0-1)
        
        Returns:
        list: Recommended repositories
        """
        # Scrape user profile if not already cached
        if username not in self.user_profiles:
            user_profile = self.scrape_user_profile(username)
            if not user_profile:
                print(f"Could not retrieve profile for {username}")
                return []
        else:
            user_profile = self.user_profiles[username]
        
        # Calculate how many recommendations to get from each source
        db_count = int(max_recommendations * (1 - web_search_ratio))
        web_count = max_recommendations - db_count
        
        all_recommendations = []
        
        # Get recommendations from database
        if self.stored_repositories and db_count > 0:
            print(f"Getting {db_count} recommendations from database...")
            db_recommendations = self.get_recommendations_from_database(user_profile, max_recommendations=db_count)
            all_recommendations.extend(db_recommendations)
        
        # Get recommendations from web search
        if web_count > 0:
            print(f"Getting {web_count} recommendations from GitHub search...")
            
            # Prepare repositories for recommendation
            candidate_repos = []
            
            # Include trending repositories based on user's top languages
            if user_profile['top_languages']:
                top_language = list(user_profile['top_languages'].keys())[0]
                trending_repos = self.scrape_trending_repositories(language=top_language)
                for repo in trending_repos:
                    detailed_repo = self.scrape_repository(repo['owner'], repo['name'])
                    if detailed_repo:
                        candidate_repos.append(detailed_repo)
            
            # If not enough candidates, search for repos based on user's top topics
            if len(candidate_repos) < web_count * 2 and user_profile['top_topics']:
                top_topic = list(user_profile['top_topics'].keys())[0]
                search_results = self.search_repositories(top_topic)
                for repo in search_results:
                    detailed_repo = self.scrape_repository(repo['owner'], repo['name'])
                    if detailed_repo and detailed_repo['owner'] != username:
                        candidate_repos.append(detailed_repo)
            
            # If still not enough, do a general search based on username
            if len(candidate_repos) < web_count * 2:
                search_results = self.search_repositories(username)
                for repo in search_results:
                    detailed_repo = self.scrape_repository(repo['owner'], repo['name'])
                    if detailed_repo and detailed_repo['owner'] != username:
                        candidate_repos.append(detailed_repo)
            
            # If have candidates, get web search recommendations
            if candidate_repos:
                # Get embedding for user preferences
                user_embedding = self.create_user_preference_embedding(user_profile)
                
                # Create embeddings for candidate repositories
                repo_embeddings = np.array([
                    self.create_project_embedding(repo) for repo in candidate_repos
                ])
                
                # Calculate similarities
                similarities = cosine_similarity([user_embedding], repo_embeddings)[0]
                
                # Get top similar repositories
                top_indices = np.argsort(similarities)[-web_count:][::-1]
                
                # Add web search recommendations
                for idx, similarity in zip(top_indices, similarities[top_indices]):
                    repo = candidate_repos[idx]
                    all_recommendations.append({
                        'owner': repo['owner'],
                        'name': repo['name'],
                        'description': repo['description'],
                        'url': repo['url'],
                        'languages': list(repo['languages'].keys()),
                        'topics': repo['topics'],
                        'similarity_score': float(similarity),
                        'stars': repo.get('stars', 0),
                        'forks': repo.get('forks', 0),
                        'from_database': False
                    })
        
        # Return the recommendations, limiting to requested number
        return all_recommendations[:max_recommendations]
    
    def clean_old_database_entries(self, days_threshold=30):
        """Clean old entries from the database based on age threshold"""
        from datetime import datetime, timedelta
        
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        # Clean repositories
        before_count = len(self.stored_repositories)
        self.stored_repositories = [
            repo for repo in self.stored_repositories
            if not ('last_updated' in repo and 
                   datetime.fromisoformat(repo['last_updated']) < threshold_date)
        ]
        
        # Clean user profiles
        profiles_before = len(self.user_profiles)
        for username in list(self.user_profiles.keys()):
            profile = self.user_profiles[username]
            if 'last_updated' in profile and datetime.fromisoformat(profile['last_updated']) < threshold_date:
                del self.user_profiles[username]
        
        # Report changes
        repos_removed = before_count - len(self.stored_repositories)
        profiles_removed = profiles_before - len(self.user_profiles)
        
        if repos_removed > 0 or profiles_removed > 0:
            print(f"Database cleaned: removed {repos_removed} repositories and {profiles_removed} user profiles")
            # Save the cleaned database
            self.save_database()
            
        return repos_removed, profiles_removed
    
    load_database = GitHubProjectRecommender.load_database
    save_database = GitHubProjectRecommender.save_database
    extract_languages_from_readme = GitHubProjectRecommender.extract_languages_from_readme
    extract_topics_from_readme = GitHubProjectRecommender.extract_topics_from_readme
    scrape_repository = GitHubProjectRecommender.scrape_repository
    _get_current_timestamp = GitHubProjectRecommender._get_current_timestamp
    scrape_user_profile = GitHubProjectRecommender.scrape_user_profile
    create_project_embedding = GitHubProjectRecommender.create_project_embedding
    create_user_preference_embedding = GitHubProjectRecommender.create_user_preference_embedding
    get_recommendations_from_database = GitHubProjectRecommender.get_recommendations_from_database
    scrape_trending_repositories = GitHubProjectRecommender.scrape_trending_repositories
    search_repositories = GitHubProjectRecommender.search_repositories
    get_recommendations_for_topic = GitHubProjectRecommender.get_recommendations_for_topic
    get_recommendations_for_user = GithubProjectRecommender.get_recommendations_for_user
    clean_old_database_entries = GitHubProjectRecommender.clean_old_database_entries