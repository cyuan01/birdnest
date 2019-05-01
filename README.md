# birdnest

The following project was designed to track the distribution of sentiments regarding all incoming tweets containing a given key word. Live tweets containing the user specified "keyword" are cleaned, scored, and graphed onto a continuously updating Plotly histogram. 

## Compiling

To run the program you will first need to make a Twitter developer account and get API keys. 
Then clone this repo and in the bird.py file, you will see at the top variables responding to each of these keys. 
From there you can replace the keyholders with your generated API keys. 
Next you will need to download the dependencies listed in the requirements.txt file
Finally, simply run Python bird.py to compile and the Dash app will run on your local server.
In the input box you can type in a keyword and press "return" to update the search query.
Note that with the standard Twitter API, requests are limited. 
