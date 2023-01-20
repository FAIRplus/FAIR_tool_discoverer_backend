FROM mongo

#ADD https://observatory.openebench.bsc.es/api/tools /tmp/tools.json
COPY tools.json /tmp/tools.json
RUN jq '.message.tools' /tmp/tools.json  > /tmp/init.json
CMD mongoimport --host mongodb --db discoverer --collection tools --type json --file /tmp/init.json --jsonArray
