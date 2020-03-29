## DBaaS execution instructions
To execute this, please follow the steps below:
1. Build the base container image (includes all the dependencies)
`cd ./base_builder && docker build -t base:latest . && cd ..`
2. Build the individual images for the persistent database, the orchestrator and the worker
`cd persdb && docker build -t persdb:latest . && cd ..`
`cd orchestrator && docker build -t orchestrator:latest . && cd ..`
`cd worker && docker build -t worker:latest . && cd ..`
3. Use docker compose to bring up the containers. (For testing purposes, one master and one slave is brought up by compose. This is supposed to be automated using docker API as part of the project)
`docker-compose up`
4. Set the master as a master role (Port can change, make sure to refer to the docker compose file)
`curl http://localhost:8101/control/v1/start/1`
5. Set the slave as a slave role (Port can change, make sure to refer to the docker compose file)
`curl http://localhost:8100/control/v1/start/2` 
6. Start making requests to the orchestrator

# Notes:
- You can change the role of a container by running (Port can change, make sure to refer to the docker compose file) :
`curl http://localhost:8100/control/v1/stop`
Followed by the new role (1 - Master, 2 - Slave) (Port can change, make sure to refer to the docker compose file)
`curl http://localhost:8100/control/v1/start/<newrole>`

