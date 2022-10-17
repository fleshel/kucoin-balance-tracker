# KuCoin Balance Tracker
A tool to track your daily balance on the KuCoin platform. 

## installation & usage

### environment variables
you need to update your environment variables prior to using. this can be done by modifying the .env file

- KUCOIN\_API_KEY=***
- KUCOIN\_API_SECRET=***
- KUCOIN\_API_PASSPHRASE=***

### external libraries
there are a few packages necessary to install prior to running.

- python_dotenv
    - used to load your api key from .env

- requests
    - used to request balance from the KuCoin API

you can install these with
`pip install python_dotenv requests` if they have not been installed already.

### usage
in order to run the application, simply enter `python3 main.py`