# FAIR Tools Discoverer Backend


The `api` directory contains the source code of the API. It is a Flask application. 

The database is a MongoDB database hosted on a remote server. 

### Database preparation
The directory `database/processing` contains scripts to process the data in the Software Observatory and insert new entries suitable for the Tool Discoverer. In addition, indexes for querying are created.

## Development

### Mongo Seed 
The directory `database/mongo-seed` contains a Dockerfile to generate a docker image of the database for development purposes. 

### Docker-compose  
The file `docker-compose-dev.yml` contains the definition of the development environment. It contains all the necessary services for development, which are the following:

```yaml
version: '3.8'

services:
  mongodb:
    container_name: mongo_dev
    image: mongo
    ports:
      - '27017:27017'

  mongo-seed:
    container_name: mongo_seed
    build: ./database/mongo-seed
    depends_on:
      - 'mongodb'
  
  prepare-data:
    container_name: prepare_data
    build: ./database/prepare-data
    depends_on:
      - 'mongo-seed'
  
  back-end:
    image: emartps/tools-discoverer-api
    restart: unless-stopped
    depends_on:
      - 'mongodb'

  front-end:
    image: emartps/tools-discoverer-nuxt
    restart: unless-stopped
    depends_on:
      - 'back-end' 
    ports:
      - '8080:80'
``` 

## Deployment 

The deployment is done through GitHub Actions. The file `github/worflows.main.yml` contains the definition of the workflow. The workflow is triggered when a new release is created. The workflow performs the following steps:
- Build of the docker images of the API application.
- Push of the images to the Docker Hub.
- Deployment of the images to the server using webhooks.