## RideShare Project
[Project Specifications](https://d1b10bmlvqabco.cloudfront.net/attach/k4vbpy4o35q1ci/jzb6kq5w25w4tm/k8py84sv1rlm/DBaaS__AMQP.pdf) 

#### When Building on a Single Instance
##### Instructions
- Start docker service
- Execute setup script ```./setup.sh```
    - Setup script builds and runs everything required. This will take a few minutes.
    - If you have no errors, RideShare is up and running!

Use the following Postman Collection to test the RideShare APIs,

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/c85f03faaffd465ae505)

##### Shutting down RideShare
- Use the cleanup spawned containers API to remove worker docker containers.
- ```Ctrl+C``` on flask terminal to stop.
- Notes
    - RabbitMQ will still be running, so shut this down manually if needed.
    - Restart by running ```docker-compose up``` in dbaas folder.
    
##### Auto Scaling
The orchestrator keeps track of the number of read requests in every 2 min.
0 – 20 requests – 1 slave container is running
21 – 40 requests – 2 slave containers are running
41 – 60 requests – 3 slave containers are running
and so on.
To test this and make requests quickly, you can use the ```./dbaas/scale_up.sh``` script. This makes 21 async read calls.




##### Debug Issues
- If you face issues in the setup, try executing the commands in the setup script one by one manually
to identify the cause of the issue.

##### Quirks (To Be Fixed)
- SyncQ Issue - Read/Write data fetched not accurate and synced across all workers
- Ignore the ```(sqlite3.IntegrityError) UNIQUE constraint failed: apicount.count ``` warning when persdb is starting up for now.
- API Count (i.e. ```/api/v1/_count```) needs to be reimplemented with new Db Structure.
