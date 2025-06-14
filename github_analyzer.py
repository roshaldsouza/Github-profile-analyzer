import os
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from collections import defaultdict
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class GitHubProfileAnalyzer:
    def __init__(self, username):
        self.username = username
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        self.user_data = None
        self.repos_data = None
        
    def fetch_user_data(self):
        """Fetch basic user information"""
        url = f"{self.base_url}/users/{self.username}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            self.user_data = response.json()
            return True
        else:
            print(f"Error fetching user data: {response.status_code}")
            return False
    
    def fetch_repos(self):
        """Fetch all repositories for the user"""
        url = f"{self.base_url}/users/{self.username}/repos?per_page=100"
        repos = []
        page = 1
        
        while True:
            response = requests.get(f"{url}&page={page}", headers=self.headers)
            if response.status_code != 200:
                print(f"Error fetching repos: {response.status_code}")
                return False
            
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        self.repos_data = repos
        return True
    
    def analyze_languages(self):
        """Analyze language usage across all repositories"""
        if not self.repos_data:
            return None
            
        language_stats = defaultdict(int)
        
        for repo in self.repos_data:
            if repo['language']:
                language_stats[repo['language']] += 1
                
        return dict(sorted(language_stats.items(), key=lambda item: item[1], reverse=True))
    
    def get_most_starred_repos(self, n=5):
        """Get the n most starred repositories"""
        if not self.repos_data:
            return None
            
        sorted_repos = sorted(self.repos_data, key=lambda x: x['stargazers_count'], reverse=True)
        return sorted_repos[:n]
    
    def generate_report(self):
        """Generate a summary report"""
        if not self.user_data or not self.repos_data:
            return None
            
        report = {
            'username': self.username,
            'profile_info': {
                'name': self.user_data.get('name', 'N/A'),
                'bio': self.user_data.get('bio', 'N/A'),
                'public_repos': self.user_data['public_repos'],
                'followers': self.user_data['followers'],
                'following': self.user_data['following'],
                'created_at': self.user_data['created_at']
            },
            'language_stats': self.analyze_languages(),
            'most_starred_repos': [
                {
                    'name': repo['name'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'url': repo['html_url']
                }
                for repo in self.get_most_starred_repos()
            ],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report
    
    def export_report(self, report, format='json'):
        """Export the report in specified format"""
        filename = f"github_report_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == 'json':
            with open(f"{filename}.json", 'w') as f:
                json.dump(report, f, indent=4)
            print(f"Report exported as {filename}.json")
        else:
            print("Only JSON export is currently supported")
    
    def visualize_languages(self, language_stats):
        """Create a pie chart of language distribution"""
        if not language_stats:
            return
            
        labels = list(language_stats.keys())
        sizes = list(language_stats.values())
        
        plt.figure(figsize=(10, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Language Distribution for {self.username}")
        plt.axis('equal')
        plt.tight_layout()
        
        # Save the figure
        filename = f"github_languages_{self.username}.png"
        plt.savefig(filename)
        print(f"Language visualization saved as {filename}")
        plt.close()
    
    def visualize_stars(self, starred_repos):
        """Create a bar chart of most starred repositories"""
        if not starred_repos:
            return
            
        repo_names = [repo['name'] for repo in starred_repos]
        stars = [repo['stars'] for repo in starred_repos]
        
        plt.figure(figsize=(10, 6))
        plt.barh(repo_names, stars, color='skyblue')
        plt.xlabel('Number of Stars')
        plt.title(f"Most Starred Repositories for {self.username}")
        plt.gca().invert_yaxis()  # Invert to show highest at top
        plt.tight_layout()
        
        # Save the figure
        filename = f"github_stars_{self.username}.png"
        plt.savefig(filename)
        print(f"Stars visualization saved as {filename}")
        plt.close()
    
    def analyze(self):
        """Run full analysis pipeline"""
        print(f"Analyzing GitHub profile for {self.username}...")
        
        if not self.fetch_user_data():
            return False
            
        if not self.fetch_repos():
            return False
            
        report = self.generate_report()
        
        if report:
            print("\n=== Profile Summary ===")
            print(f"Name: {report['profile_info']['name']}")
            print(f"Bio: {report['profile_info']['bio']}")
            print(f"Public Repos: {report['profile_info']['public_repos']}")
            print(f"Followers: {report['profile_info']['followers']}")
            print(f"Following: {report['profile_info']['following']}")
            print(f"Account Created: {report['profile_info']['created_at']}")
            
            print("\n=== Top Languages ===")
            for lang, count in report['language_stats'].items():
                print(f"{lang}: {count} repos")
                
            print("\n=== Most Starred Repositories ===")
            for repo in report['most_starred_repos']:
                print(f"{repo['name']}: {repo['stars']} stars")
            
            # Export and visualize
            self.export_report(report)
            self.visualize_languages(report['language_stats'])
            self.visualize_stars(report['most_starred_repos'])
            
            return True
        return False


if __name__ == "__main__":
    username = input("Enter GitHub username: ")
    analyzer = GitHubProfileAnalyzer(username)
    analyzer.analyze()