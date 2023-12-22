# FAIR Tools Discoverer Backend

[![build and push](https://github.com/FAIRplus/FAIR_tool_discoverer_backend/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/FAIRplus/FAIR_tool_discoverer_backend/actions/workflows/main.yml)
 [![Docker Image Version (latest semver)](https://img.shields.io/docker/v/emartps/tools-discoverer-api?sort=semver)](https://hub.docker.com/r/emartps/tools-discoverer-api)
[![License](https://img.shields.io/github/license/FAIRplus/FAIR_tool_discoverer_backend)](https://github.com/FAIRplus/FAIR_tool_discoverer_backend/blob/main/LICENSE.md) 

This repository contains the source code of the backend of the FAIR Tools Discoverer. The backend is composed of two parts: the database and the API. In addition, the repository contains the scripts to process the data in the Software Observatory and insert new entries suitable for the Tool Discoverer.
-  The `api` directory contains the source code of the API.
-  The `database/prepare-data` directory contains the scripts to process the data in the Software Observatory and insert new entries suitable for the Tool Discoverer. In addition, indexes for querying are created.
- The `database/mongo-seed` directory contains a Dockerfile to generate a docker image of the database for development purposes.


## API 

### Usage 

The API is available at https://fair-tool-discoverer.bsc.es/api. The endpoints of the API are descibed in the [Documentation](https://fair-tool-discoverer.bsc.es/api/docs). 

### Development 

The API is developed using Python and the [FastAPI](https://fastapi.tiangolo.com/) framework. 

#### Native installation 

To install the API locally, it is recommended to use a virtual environment. The following commands install the API in a virtual environment and run it:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The database connection details are set through environment variables:

| Parameter | Description | 
| --- | --- |
| MONGO_HOST | Host of the database |
| MONGO_PORT | Port of the database |
| MONGO_USER | User of the database |
| MONGO_PWD | Password of the database |
| MONGO_AUTH_SRC | Name of the authentication database |
| MONGO_DB | Name of the database |
| DISCOV_COLLECTION | Name of the collection where the metadata for the discoverer is stored |
| RESULTS_COLLECTION | Name of the collection where the results of the queries are stored |

#### Docker installation

The API is available as a Docker image at [Docker Hub](https://hub.docker.com/r/emartps/tools-discoverer-api). The following command runs the API in a Docker container: 

```bash
docker run -d -p 8000:8000 --env-file .env -v /path/to/host/log/directory:/app/logs/ emartps/tools-discoverer-api:latest 
``` 

The environment variables are set in the `.env` file. The following is an example of the content of the file:

```bash
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_USER=tools-discoverer
MONGO_PWD=tools-discoverer
MONGO_AUTH_SRC=admin
MONGO_DB=tools-discoverer
DISCOV_COLLECTION=discoverer
RESULTS_COLLECTION=results
``` 

#### Using a mock database in a Docker and docker-compose  

The API can be run with a mock database in a Docker container. The mock database is generated from the data in the Software Observatory. A seed database for development purposes can be build with the Dockerfile in `database/mongo-seed`. 

The file `docker-compose-dev.yml` contains the definition of the development environment. It contains all the necessary services for development, which are the following:

## CI/CD

The deployment is done through GitHub Actions. The file `github/worflows.main.yml` contains the definition of the workflow. The workflow is triggered manually. The workflow performs the following steps:
- 1. Build of the docker images of the API application.
- 2. Push of the images to the Docker Hub.

