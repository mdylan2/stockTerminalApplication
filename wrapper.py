import requests
import json
import pandas as pd
import view

'''
Markit class to deal with API calls
Can search for companies using company name, get quotes for tickers, and get current prices for tickers
'''
class Markit:
	'''
	Initializing the URLS to request
	'''
	def __init__(self):
		self.lookup_url = "http://dev.markitondemand.com/Api/v2/Lookup/json"
		self.quote_url = "http://dev.markitondemand.com/Api/v2/Quote/json"

	'''
	Returns a dataframe of companies, tickers, and exchanges that match an input of company name
	'''
	def company_search(self,string):
		param = dict(
			input = string.strip().lower()
		)
		request = requests.get(self.lookup_url,params = param)
		if request.status_code != 200:
			print(view.faultyCode(string))
			return pd.DataFrame()
		request = request.json()
		return pd.DataFrame.from_records(request)

	'''
	Returns information about a ticker (lastprice, timestamp, etc) in a dictionary format.
	Information is specified by the user
	'''
	def get_quote(self,string, *args):
		param = dict(
			symbol = string.strip().upper()
		)
		request = requests.get(self.quote_url,params = param)
		if request.status_code != 200:
			print(view.faultyCode(string.strip().upper()))
			return {}
		request = request.json()
		try:
			data = {key:request[key] for key in args}
			return data
		except KeyError:
			return {}
	
	'''
	Returns the up to date price of a stock ticker
	'''
	def get_price(self,string):
		data = self.get_quote(string,'LastPrice')
		if data == {}:
			print(view.faultyCode(string.strip().upper()))
			return 0
		return data['LastPrice']