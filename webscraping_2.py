import requests
import base64


class webscrape:
    def get_repo_names_from_target_name(target_name : str) -> list:
        def get_user_repos(username, token=None):
            url = f"https://api.github.com/users/{username}/repos"
            headers = {"Authorization": f"token {token}"} if token else {}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                repos = response.json()
                return [repo["full_name"] for repo in repos]
            else:
                return {"error": f"Failed to fetch repositories: {response.status_code}"}

        # Function to get repositories the user has contributed to
        def get_contributed_repos(username, token=None):
            url = f"https://api.github.com/users/{username}/events"
            headers = {"Authorization": f"token {token}"} if token else {}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                events = response.json()
                contributed_repos = set()

                for event in events:
                    if event["type"] in ["PushEvent", "PullRequestEvent", "IssuesEvent"]:
                        contributed_repos.add(event["repo"]["name"])

                return list(contributed_repos)
            else:
                return {"error": f"Failed to fetch contributed repositories: {response.status_code}"}
        owned_repos = get_user_repos(target_name)
        contributed_repos = get_contributed_repos(target_name)
        for i in contributed_repos:
            if i not in owned_repos:
                owned_repos.append(i)
        l = []
        for i in owned_repos:
            l.append("/"+i)
        return l

    def get_repo_readme(urls : list) -> dict:
        def get_repo_readme_for_one_url(owner, repo, token=None):
            """
            Fetches the README file from a given GitHub repository.

            :param owner: GitHub username or organization
            :param repo: Repository name
            :param token: (Optional) GitHub personal access token for authentication
            :return: Decoded README content or an error message
            """
            url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            headers = {"Authorization": f"token {token}"} if token else {}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                readme_content = base64.b64decode(data["content"]).decode("utf-8")
                return readme_content
            else:
                return f"Error: Unable to fetch README. Status Code: {response.status_code}, Message: {response.json().get('message', 'Unknown error')}"
        dic = {}
        for i in urls:
            dic[i] = get_repo_readme_for_one_url(owner=i.split("/")[-2],repo=i.split("/")[-1])
        return dic

    def get_commits_from_repo_url(url : str) -> dict:
        def get_repo_contributors(owner, repo, token=None):
            """
            Fetches the list of contributors to a given GitHub repository.

            :param owner: GitHub username or organization
            :param repo: Repository name
            :param token: (Optional) GitHub personal access token for authentication
            :return: List of contributors with their contribution count
            """
            url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            headers = {"Authorization": f"token {token}"} if token else {}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                contributors = response.json()
                contributor_list = [
                    {"username": user["login"], "contributions": user["contributions"], "profile_url": user["html_url"]}
                    for user in contributors
                ]
                return contributor_list
            else:
                return f"Error: Unable to fetch contributors. Status Code: {response.status_code}, Message: {response.json().get('message', 'Unknown error')}"
        dic = {}
        for i in get_repo_contributors(owner=url.split("/")[-2],repo=url.split("/")[-1]):
            dic[i["username"]] = i["contributions"]
        return dic

    def search_result_from_query(query,max_recommendations=5):
        def search_github_repos(keyword, max_results=5, token=None):
            """
            Searches GitHub repositories based on a keyword.

            :param keyword: Search query
            :param max_results: Number of results to return (default is 5)
            :param token: (Optional) GitHub personal access token for authentication
            :return: List of top repositories matching the keyword
            """
            url = f"https://api.github.com/search/repositories?q={keyword}&per_page={max_results}"
            headers = {"Authorization": f"token {token}"} if token else {}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                results = [
                    {
                        "name": repo["name"],
                        "owner": repo["owner"]["login"],
                        "stars": repo["stargazers_count"],
                        "language": repo["language"],
                        "url": repo["html_url"]
                    }
                    for repo in data["items"]
                ]
                return results
            else:
                return f"Error: Unable to fetch search results. Status Code: {response.status_code}, Message: {response.json().get('message', 'Unknown error')}"
        l = []
        for i in search_github_repos(keyword=query,max_results=max_recommendations):
            l.append(i["url"])
        return l


if __name__ == "__main__":
    print(webscrape.search_result_from_query("hello"))