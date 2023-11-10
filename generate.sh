#!/bin/bash
docker build . -t sdmtib/sdg:latest
docker run --name SDG -v ./data:/data -d sdmtib/sdg:latest
sleep 5s
docker exec -it SDG bash -c "SDG -n $1 -p $2"
docker rm -fv SDG
