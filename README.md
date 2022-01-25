# BlockchainScan
## RUN
* Create .env.db file
  * POSTGRES_USER
  * POSTGRES_PASSWORD
  * POSTGRES_DB
* Create .env file
  * DEBUG=0
  * SECRET_KEY
  * POSTGRES_ENGINE=django.db.backends.postgresql_psycopg2
  * POSTGRES_DB=blockchain_scan
  * POSTGRES_USER
  * POSTGRES_PASSWORD
  * POSTGRES_HOST=blockchain_scan_database
  * POSTGRES_PORT=5432
  * JWT_SECRET
  * BSC_API_KEY
  * ETH_API_KEY
  * POLYGON_API_KEY
  * INFURA_URL
  * MORALIS_BASE_URL
  * MORALIS_API_KEY
  * BOT_TOKEN
  * BASE_SERVER_URL=http://api:8000/api
  * BASE_SERVER_WS=ws://api:8000/ws
  * CELERY_BROKER_URL=redis://redis:6379/0
  * ADMINS
  * SERVER_API_KEY


## TODO LIST
* add logging sentry
* add ssl sertificate
