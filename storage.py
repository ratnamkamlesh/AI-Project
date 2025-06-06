import json
import os

def get_user_dir(username):
    dir_path = os.path.join("user_data", username)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def save_query(username, query, response,response_time=None):
    user_dir = get_user_dir(username)
    file_path = os.path.join(user_dir, "query_log.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append({"query": query, "response": response,"response_time": response_time})
    with open(file_path, "w") as f:
        json.dump(data, f)

def get_query_history(username):
    file_path = os.path.join("user_data", username, "query_log.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []
