# IBKR-Dashboard
Docker Compose for creating a IBKR Dashboard which includes risk data and current positions

# Containers
Consists of three containers
* [ibeam](https://github.com/Voyz/ibeam) - With some modifications for a headless API Gateway enabling authenticating to Interactive Brokers Web API
  * Created by [Voyz](https://github.com/Voyz) with modifications made by me for service discovery across external containers
* ibkr-api-parser - parses the IBKR API and returns to formatted html
* ibkr-dashboard - the web interface consisting of the risk and position data
