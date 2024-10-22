
# GitMazon Image Producer

Builds Docker images for users' repositories and notifies the corresponding worker node to start the service.

## Technique 

- Utilized **Flask** as a webhook server to handle registration events from the MasterNode and push events from GitHub.
- Executed **Shell Scripts** to build Docker images for users and pushed them to DockerHub.
- 


