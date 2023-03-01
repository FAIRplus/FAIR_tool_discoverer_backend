# Discoverer Database construction

The database is a MongoDB database. It is hosted on a remote server. The directory `database/processing` contains scripts to process tools metadata and insert new entries suitable for the Tool Discoverer.  In addition, indexes for querying are created. 
The file `config.ini` contains the databse connection detail. The required parameters are the following:

| Parameter | Description | 
| --- | --- |
| DBHOST | Host of the database |
| DBPORT | Port of the database |
| DATABASE | Name of the database |
| COLLECTION | Name of the collection where the original metadata is stored |
| DISCOV_COLLECTION | Name of the collection where the metadata for the discoverer is stored |

## For development
This directory contains two containers that initialize and populate the database. The first one is a MongoDB database populated with the tools collection of the software Observatory. The second one is a container that processes the data from the Software Observatory and inserts it into the database. In total, three services: 
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
    build: ./mongo-seed
    depends_on:
      - 'mongodb'
  
  prepare-data:
    container_name: prepare_data
    build: ./prepare-data
    depends_on:
      - 'mongo-seed'
```