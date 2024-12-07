import sys
import json
import urllib.request
import urllib.error
import os
import time

CACHE_DIR = "./cache"
CACHE_EXPIRY = 60 * 5  # Cache expiry in seconds (5 minutes)

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def fetch_github_activity(username):
    """
    Fetch recent activity of the given GitHub username.
    Implements caching to reduce redundant API calls.
    """
    cache_path = os.path.join(CACHE_DIR, f"{username}_events.json")
    
    # Check if cache exists and is valid
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < CACHE_EXPIRY:
        with open(cache_path, 'r') as cache_file:
            print("Loading cached data...")
            return json.load(cache_file)

    # Fetch data from GitHub API
    api_url = f"https://api.github.com/users/{username}/events"
    try:
        with urllib.request.urlopen(api_url) as response:
            data = response.read().decode('utf-8')
            events = json.loads(data)
            # Cache the result
            with open(cache_path, 'w') as cache_file:
                json.dump(events, cache_file)
            return events
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason} for user {username}."
    except urllib.error.URLError as e:
        return f"Network Error: {e.reason}."
    except json.JSONDecodeError:
        return "Failed to parse the API response."


def fetch_user_info(username):
    """
    Fetch additional information about the GitHub user.
    """
    api_url = f"https://api.github.com/users/{username}"
    try:
        with urllib.request.urlopen(api_url) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.reason} for user {username}."
    except urllib.error.URLError as e:
        return f"Network Error: {e.reason}."
    except json.JSONDecodeError:
        return "Failed to parse the API response."


def display_activity(events, filter_type=None):
    """
    Display recent GitHub activity with optional filtering by event type.
    """
    if isinstance(events, str):
        print(events)
        return

    if not events:
        print("No recent activity found.")
        return

    filtered_events = [event for event in events if filter_type is None or event.get("type") == filter_type]
    if not filtered_events:
        print(f"No activities found for the event type: {filter_type}")
        return

    print("\nRecent Activity:")
    for event in filtered_events[:10]:  # Limit to 10 entries
        event_type = event.get("type")
        repo_name = event.get("repo", {}).get("name", "Unknown repository")
        action_message = interpret_event(event_type, repo_name)
        print(f"  - {action_message}")


def display_user_info(user_info):
    """
    Display structured information about the user.
    """
    if isinstance(user_info, str):
        print(user_info)
        return

    print("\nUser Information:")
    print(f"  Name: {user_info.get('name', 'N/A')}")
    print(f"  Bio: {user_info.get('bio', 'N/A')}")
    print(f"  Public Repos: {user_info.get('public_repos', 0)}")
    print(f"  Followers: {user_info.get('followers', 0)}")
    print(f"  Following: {user_info.get('following', 0)}")
    print(f"  Profile: {user_info.get('html_url', 'N/A')}")


def interpret_event(event_type, repo_name):
    """
    Generate a user-friendly message based on the event type.
    """
    if event_type == "PushEvent":
        return f"Pushed commits to {repo_name}."
    elif event_type == "IssuesEvent":
        return f"Opened an issue in {repo_name}."
    elif event_type == "WatchEvent":
        return f"Starred {repo_name}."
    elif event_type == "ForkEvent":
        return f"Forked {repo_name}."
    elif event_type == "PullRequestEvent":
        return f"Opened a pull request in {repo_name}."
    else:
        return f"Performed {event_type} in {repo_name}."


def main():
    """
    Entry point of the application.
    Handles CLI arguments and executes logic.
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: github-activity <username> [event_type]")
        sys.exit(1)

    username = sys.argv[1]
    filter_type = sys.argv[2] if len(sys.argv) == 3 else None

    print(f"Fetching activity for GitHub user: {username}...")

    user_info = fetch_user_info(username)
    display_user_info(user_info)

    events = fetch_github_activity(username)
    display_activity(events, filter_type)


if __name__ == "__main__":
    main()
