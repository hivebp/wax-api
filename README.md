# WAX NFT API

Welcome to the univeral WAX NFT API, an API that provides information on all NFTs on the WAX Blockchain, including 
simpleassets and atomicassets, as well as the most smart contracts around NFTs such a drops, packs, crafting and 
market contract. Use this API to get current NFT listings, drops and sales history, PFP traits analytics, sets and much 
more. 

## Requirements

* Python >= 3.10
* PostgreSQL >= 14.0
* eos-chronicle > 3.0

## Configuration
* Open config.py to enter the IP and PORT on which chronicle is running.
* Edit the list of smart contracts in config.py you wish to follow
* Edit chronicle-config/config.ini to add the host and port of your state history API. Also change the list of smart 
contracts to follow and to setup host and port of your chronicle instance. The list of contracts should be the same as
in your config.py.

## Installation
* Clone this repository and navigate into it.
* Run ```python3.10 -m venv env```
* Run ```source env/bin/activate```
* Run ```pip install -r requirements.txt```
* Run ```deactivate```
* Switch to your postgres profile and create a database:
  * Run ```su - postgres``` 
  * Run ```psql```
  * Run ```CREATE DATABASE your_database```
* If you're using a snapshot, import the snapshot with ```psql your_database < /path/to/the/snapshot.sql```, otherwise import db_schema.sql with ```psql your_database < /path/to/wax-api/db_schema.sql```
* Install Chronicle from https://github.com/EOSChronicleProject/eos-chronicle 
* Create a chronicle job like ```vi /etc/systemd/system/chronicle.service```
* Add the following content:
```
Description=Run Chronicle

[Service]
Type=simple
ExecStart=/usr/local/sbin/chronicle-receiver --config-dir=/path/to/wax-api/chronicle-config --data-dir=/path/to/chronicle-data
Restart=always
RestartSec=10
KillMode=process

[Install]
WantedBy=multi-user.target
```
* Create a job for the chronicle consumer ```vi /etc/systemd/system/consumer.service```
* Add the following content:
```
Description=Chronicle Consumer

[Service]
Type=simple
ExecStart=/path/to/wax-api/env/bin/python /path/to/wax-api/chronicle_consumer.py

Restart=always
RestartSec=10
KillMode=process
Environment="DB=postgresql://root:DB_PASSWORD@0.0.0.0:5432/<your_database>"

[Install]
WantedBy=multi-user.target
```
* Create a job for the filler ```vi /etc/systemd/system/filler.service```
* Add the following content:
```
Description=WAX API Filler

[Service]
Type=simple
ExecStart=/path/to/wax-api/env/bin/python /path/to/wax-api/filler.py

Restart=always
RestartSec=10
KillMode=process
Environment="DB=postgresql://<user>:DB_PASSWORD@0.0.0.0:5432/<your_database>"

[Install]
WantedBy=multi-user.target
```
* Create a job for the API ```vi /etc/systemd/system/api.service```
* Add the following content:
```
Description=WAX API Service

[Service]
Type=simple
ExecStart=/path/to/wax-api/env/bin/python /path/to/wax-api/api.py

Restart=always
RestartSec=10
KillMode=process
Environment="DB=postgresql://<user>:DB_PASSWORD@0.0.0.0:5432/<your_database>"

[Install]
WantedBy=multi-user.target
```

### Start
Run ```curl -L 0.0.0.0:5002/filler/start``` to start the filler and ```curl -L 0.0.0.0:5002/filler/stop``` to stop.


### Scheduling
* Run ```crontab -e```
* Depending on your needs, add the following commands:
```
*/10 * * * * curl -L 0.0.0.0:5002/loader/refresh-drops-views
*/5 * * * * curl -L 0.0.0.0:5002/loader/refresh-recently-sold
*/10 * * * * curl -L 0.0.0.0:5002/loader/update-floor-prices
*/30 * * * * curl -L 0.0.0.0:5002/loader/update-estimated-wax-price
*/15 * * * * curl -L 0.0.0.0:5002/loader/update-template-stats
0 */6 * * * curl -L 0.0.0.0:5002/loader/update-big-volumes
0 8 * * * curl -L 0.0.0.0:5002/loader/update-collection-user-stats
*/5 * * * * curl -L 0.0.0.0:5002/loader/update-small-volumes
*/15 * * * * curl -L 0.0.0.0:5002/loader/update-pfp-attributes
*/1 * * * * curl -L 0.0.0.0:5002/loader/update-rwax-assets
*/10 * * * * curl -L 0.0.0.0:5002/loader/sync-new-collection-verifications
*/5 * * * * curl -L 0.0.0.0:5002/loader/update-template-stats
```

### API Documentation

Find the API Documentation here:


### Snapshots

Download the full snapshot here:

[snapshot_wax_api_341065560](https://download.hivebp.io/snapshots/snapshot_wax_api_341065560.tar.gz)

Import the snapshot with these commands:
* ```tar -xvf snapshot_wax_api_341065560.tar.gz```
* ```su - postgres```
* ```psql your_database < /path/to/the/snapshot_wax_api_341065560.sql```

