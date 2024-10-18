from flask import Flask, request, jsonify, make_response
import subprocess
import os
import requests
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def check_repo_files(repo_owner, repo_name):
    # GitHub API endpoint to fetch repo contents
    github_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"

    # Fetch repo content
    response = requests.get(github_api_url)

    if response.status_code == 200:
        repo_contents = response.json()
        # Check if 'src' folder and 'pom.xml' exist in repo
        src_exists = any(item['name'] == 'src' and item['type'] == 'dir' for item in repo_contents)
        pom_exists = any(item['name'] == 'pom.xml' and item['type'] == 'file' for item in repo_contents)

        if src_exists and pom_exists:
            return True, "Both 'src' folder and 'pom.xml' file exist."
        else:
            missing_items = []
            if not src_exists:
                missing_items.append('src folder')
            if not pom_exists:
                missing_items.append('pom.xml file')
            return False, f"缺少必要檔案: src 目錄以及 pom.xml 檔案"
    else:
        return False, f"Failed to fetch repo contents. Status code: {response.status_code}, Error: {response.text}"

@app.route('/deploy', methods=['POST'])
def deploy():
    try:
        payload = request.json
        repo_owner = payload.get('repository', {}).get('owner',{}).get('login')
        repo_name = payload.get('repository', {}).get('name')

        # Check if the repo contains 'src' folder and 'pom.xml' file
        files_exist, message = check_repo_files(repo_owner, repo_name)
        if not files_exist:
            response = {'error': message }
            return jsonify(response), 400

        repo_name_lower = repo_name.lower()

        script_path = '/home/ubuntu/CodeCheckoutAndImageBuild.sh'

        result = subprocess.run(['/bin/sh', script_path, repo_owner, repo_name],
                                capture_output=True,
                                text=True,
                                check=True)

        notify_service_server(repo_owner,repo_name,repo_name_lower)

        return jsonify({"message": "Deployment script executed successfully."}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "服務建立失敗，請檢查是否符合系統規範"}), 400
    except RuntimeError as e:
        return jsonify({"error": "服務註冊失敗，無法啟動使用者服務"}), 400

def notify_service_server(repo_owner, repo_name, repo_name_lower):
    # Get Worker Node IP from Master Node /info api
    master_node_url = f"http://52.69.33.14:8082/info?username={repo_owner}&repoName={repo_name}"
    master_node_response = requests.get(master_node_url)
    worker_node_data = master_node_response.json()
    worker_node_ip = worker_node_data.get("podIP")

    print('this is worker node ip', worker_node_ip);

    service_server_url = f"http://{worker_node_ip}:8081/deploy"
    data = {
            'repository_owner': repo_owner,
            'repository_name': repo_name,
            'repository_name_lower': repo_name_lower
    }
    response = requests.post(service_server_url, json=data)
    response.raise_for_status()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
