## RideShare Project - Cloud Ready
[Project Specifications](https://d1b10bmlvqabco.cloudfront.net/attach/k4vbpy4o35q1ci/jzb6kq5w25w4tm/k8py84sv1rlm/DBaaS__AMQP.pdf) 

## Cloud Deployment

### User's VM

1. Copy the `UsersInstance` folder into the Users VM.

2. Open the `docker-compose.yml` present inside the folder.

3. Update the `ORCHHOST` environment variable to either the DNS Entry or the IP address of the Orchestrator VM.

4.  Install docker-compose and run:

   `docker-compose up -d`

### Rides VM

1. Copy the `RidesInstance` folder into the Rides VM.

2. Open the `docker-compose.yml` present inside the folder.

3. Update the `ORCHHOST` environment variable to either the DNS Entry or the IP address of the Orchestrator VM.

4. Update the `MYHOST` environment variable to either the DNS Entry or the IP address of the Rides VM.

5. Update the `BALANCER` environment variable to the DNS entry of the path based load balancer.

6. Install docker-compose and run:

   `docker-compose up -d`

### Orchestrator VM

1. Copy the `dbaas` folder into the Orchestrator VM.
2. Copy the startup script `startup.sh` to the same directory as the folder.
3. Execute the script using bash to automatically perform all the needed tasks to deploy the orchestrator.

