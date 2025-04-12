import os

cache_path = os.path.join(os.path.expanduser("~"), ".winpick", "github_token.json")
if os.path.exists(cache_path):
    os.remove(cache_path)
    print("Cache file removed successfully")
else:
    print("Cache file does not exist")