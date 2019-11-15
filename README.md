# Visulate for Oracle
Visulate for Oracle is an Oracle data dictionary browsing service to help data engineers understand the structure and dependencies in Oracle databases that they plan to migrate to the Cloud.

## Functionality
A registration file stores connection details for one or more the databases.  Visulate queries the data dictionary for each connection and allows the user to browse the result. 

![Alt text](/screenshots/object-selection.png?raw=true "Visulate for Oracle database object selection")

A report is generated for each database object by querying the appropriate dictionary views (e.g. DBA_TABLES and other views for table objects or DBA_SOURCE for packages)  

![Alt text](/screenshots/object-details.png?raw=true "Visulate for Oracle object details")

This report also queries database's dependency model to identify dependencies to and from the object (e.g a view "uses" the tables it is based on and is "used by" a procedure that selects from it).  The dependency info identifies line numbers for references that appear in stored procedures.

![Alt text](/screenshots/object-dependencies.png?raw=true "Visulate for Oracle object dependencies")

## Implementation
Visulate for Oracle exposes REST endpoints and a UI to browse the metadata for registered connections. The API server is implemented in Express and uses node-oracledb to connect to the database(s).  Connections are registered in a configuration file (database.js) located in the config directory. A separate file (http-server.js) in the same directory controls the behavior of the Express server.

The start point for the Express server is app.js.  Most of the source code is in the services directory. Registered databases  must connect to a user with the SELECT ANY DICTIONARY privilege. The setup directory includes a script to create a user with the minimum required privileges. The SYSTEM account would also work (in a non-production environment) or you can grant SELECT ANY DICTIONARY to an existing user.

An Angular UI makes API calls to the Express server and displays the result. The source code for this is in the client directory. It reads the apiBase property in the `src/environments/environment.ts` (or environment.prod.ts) file to identify the base url for API calls. 

The API server supports cross origin (CORS) requests from locations identified in the `config/http-server.js` file.  The default configuration accepts requests from localhost:4200.  The configuration file can be edited to support other locations.

## Setup Instructions (Development Environment)
1. Clone the repo
2. Run `npm install` in the project root and client directories 
3. Follow the instruction in https://oracle.github.io/node-oracledb/INSTALL.html#quickstart to install node-oracledb.
4. Use the script in the setup directory to setup a database user with the SELECT ANY DICTIONARY privilege in each database you want to register.
5. Edit the `config/database.js` file to register the databases
6. (Optional) edit the `config/http-server.js` file to change the port number and Angular client location
7. Run `npm start` in the project root to start the API server.
8. Make an API call to test the configuration e.g. `curl localhost:3000/api` or `curl localhost:3000/api | json_pp`
9. (Optional) edit the `src/environments/environment.ts` file if the API server is running on a different port.
9. Run `ng serve` from the client directory to start the Angular client
9. Navigate to `localhost:4200` in a browser window to view the result.

## Testing
1. Run `npm test` from the project root to test the API server
2. Run `ng test` from the client directory to run unit tests for the client

## Deployment
1. Review apiBase value in `visulate-for-oracle/client/src/environments/environment.ts` and edit to match the API server deployment value 
2. Build the docker images:
```
docker build --rm -t visulate-server:latest .
docker build --rm -t visulate-client:latest ./client
```
3. Deploy the images:
```
docker run -d -p 3000:3000/tcp visulate-server:latest
docker run -d -p 80:80/tcp visulate-client:latest
```
4. (Optional) bind the log file directories to a persistent volume (e.g /var/log/<dir>)
```
docker run -d -p 3000:3000/tcp -v /var/log/visulate-server:/visulate-server/logs visulate-server:latest
docker run --rm -d -p 80:80/tcp -v /var/log/visulate-client:/var/log/nginx visulate-client:latest
```
5. (Optional) Copy the `visulate-for-oracle/config` files to a staging directory before starting the server. This will allow you to edit the database registration file without rebuilding the image. Example:
```
docker run -d -p 3000:3000/tcp -v /var/log/visulate-server:/visulate-server/logs -v /home/pgoldtho/config:/visulate-server/config visulate-server:latest

```
