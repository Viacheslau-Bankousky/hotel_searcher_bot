# Hotels_Searcher_bot

![my_bot](https://www.botmake.ru/assets/img/demo/USSCBOT.jpg)

### This Telegram bot is designed for easy search of hotels via the API hotels.com
***
### Basic commands of the bot:
* `/start` – start and restart the bot;
* `/lowprice` –search for hotels with a minimum cost;
* `/highprice` – search for hotels with the maximum cost;
* `/bestdeal` – search for hotels that are most suitable for 
distance from the city center and cost;
* `/history` – displays the search history.
###### note: 
    you can enter either manually at any time, or by pressing the menu button 
    and then selecting the appropriate command in the inline keyboard.
### Additional command:
* `/help` – displays the message that you should use the "menu"
button to get information about all available bot commands 
###### note:
    you can only enter it manually at any time

### Getting started
#### To launch the bot's code, you need:
* Clone the repo (`git clone https://gitlab.skillbox.ru/Bankousky_Viacheslau/python_basic_diploma.git`)
* `cd` into the new directory `python_basic_diploma`
* Create a new virtual environment `venv` in the directory (`python -m virtualenv venv`)
* Activate the new environment (`source venv/bin/activate`)
* Install dependencies in new environment (`pip install -r requirements.txt`);
* Create the file .env in the root project directory where you will save RAPIDAPI_KEY and token from your bot
(example file in `.env.template`).


