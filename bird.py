import json
import tweepy
import numpy as np
import re
from afinn import Afinn

import os
from flask import Flask, render_template, json, url_for

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

from dash.dependencies import Output, Input, State

import plotly.figure_factory as ff

global keyword
keyword = '____'

global y_data
y_data = []

afinn = Afinn()

# Enter your keys/secrets as strings in the following fields
credentials = {}  

credentials['CONSUMER_KEY'] = "YOUR_CONSUMER_KEY" 
credentials['CONSUMER_SECRET'] = "YOUR_CONSUMER_SECRET"  
credentials['ACCESS_TOKEN'] = "YOUR_ACCESS_TOKEN"  
credentials['ACCESS_SECRET'] = "YOUR_ACCESS_SECRET"

# Save the credentials object to file
with open("twitter_creds.json", "w") as file:  
	json.dump(credentials, file)

with open("twitter_creds.json", "r") as file:
	creds = json.load(file)

auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])
auth.set_access_token(creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])
api = tweepy.API(auth)

def remove_pattern(input_txt, pattern):
	r = re.findall(pattern, input_txt)
	for i in r:
		input_txt = re.sub(i, '', input_txt)        
	return input_txt


def clean_tweets(lst):
	# remove twitter Return handles (RT @xxx:)
	lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
	# remove twitter handles (@xxx)
	lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
	# remove URL links (httpxxx)
	lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
	# remove special characters, numbers, punctuations (except for #)
	lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
	
	return lst

class MyStreamListener(tweepy.StreamListener):
	def on_status(self, status):

		data = json.dumps(status._json)
		data_json = json.loads(data)

		# want to know if the tweet was not quoted, but truncated is false
		# if it was retweeted and truncated is false

		test1 = 'retweeted_status' in data_json
		test2 = 'extended_tweet' in data_json
		test3 = data_json['truncated']

		text = ''

		if (test1 == True and test3 == False and data_json["retweeted_status"]["truncated"] == True):
			text = data_json["retweeted_status"]["extended_tweet"]["full_text"]

		elif (test3 == True and test2 == True):
			text = data_json["extended_tweet"]["full_text"]

		else:
			text = data_json["text"]

		clean_text = str(clean_tweets(text))

		length = len(clean_text.split())

		score = afinn.score(clean_text) / length

		global y_data

		score_float = float(score)
		score_float = round(score_float, 3)

		y_data.append(score_float)

	def on_error(self, status_code):
		print(status_code)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=MyStreamListener())

app = dash.Dash(__name__)

app.layout = html.Div(
	[
		dcc.Graph(id='live-graph', animate = False),
		dcc.Interval(
			id = 'interval-component',
			interval = 1000,
			n_intervals = 0
			),
		dcc.Input(id='input-1', type='text', value="Enter a search query!"),
    	html.Div(id='user_input')

		]
	)

@app.callback(

		Output('user_input', 'children'),
		[Input('input-1', 'n_submit')],
		[State('input-1', 'value')]
	)
def update_output(ns1, input1):
	global keyword
	keyword = input1

	print(keyword)

	global y_data
	y_data.clear()
	myStream.disconnect()
	myStream.filter(track=[keyword], languages=['en'], is_async=True)


@app.callback(Output('live-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):

	data = go.Histogram(
			x=list(y_data),
			name= "Total '" + keyword + "' tweets = " + str(len(y_data)),
			histnorm = 'probability',
			opacity=0.5,
			marker = dict(color = "#00ffa1")
		)

	return {'data' : [data], 'layout' : go.Layout(title = "Sentiment Analysis of Tweets containing the word '" + keyword + "'",
			xaxis = dict(range=[-1, 1], title = "Sentiment Score"), yaxis = dict(title = "Probability"), showlegend=True)}

if __name__ == "__main__":
	app.run_server(debug=False)



