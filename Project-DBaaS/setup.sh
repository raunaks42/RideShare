docker network create dbaas-net
cd ./RidesInstance && docker-compose up -d && cd ..
cd ./UsersInstance && docker-compose up -d && cd ..
cd dbaas || exit
docker run -d --name bunny --network dbaas-net rabbitmq
sleep 20
cd base_builder && docker build -t base:latest . && cd ..
cd worker && docker build -t worker:latest . && cd ..
docker-compose up
cd ..