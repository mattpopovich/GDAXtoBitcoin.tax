# Current Input: 
# TIMESTAMP,				ACCOUNT NAME,TYPE,		BALANCE,		 AMOUNT,CURRENCY,EQUIV USD,			ID
# 2015-07-06T01:24:51+00:00,USD,		 transfer,  0.00010330737575,5.0,	USD,	 5.0,				13530470
# 2015-07-12T16:52:51+00:00,USD,		 match,		0.00010330737575,-3.1,	USD,     -3.1,				14767258
# 2015-07-12T16:52:51+00:00,BTC,		 match,		0.0,			 0.01,	BTC,	 3.0561000000000003,14767257
# 2015-07-13T03:10:57+00:00,USD,		 transfer,	0.00010330737575,378.09,USD,	 378.09,			14855962

# Desired Output: 
# Date,                     Action,Source,Symbol,Volume,Price,Currency,Fee
# 2014-01-01 13:00:00 -0800,BUY,   Online,BTC,   1,     500,  USD,     5.50


# Following bitcoin.tax's CSV import feature
class BtaxTrade: 

	# Description of members
	# source = optional
	# action = BUY, SELL, FEE
	# Symbol = BTC, LTC, DASH, etc
	# Volume = number of coins traded - ignore if FEE
	# Currency = USD, BTC, LTC, etc
	# Price = price per coin in Currency or blank for lookup - ignore if FEE
	# Fee = any additional costs of the trade
	# FeeCurrency = currency of fee if different than Currency

	rows = ['Date', 'Action', 'Source', 'Symbol', 'Volume', 'Price', 'Currency', 'Fee']
	@staticmethod
	def header():
		ret = '' 
		for i in range(0, len(BtaxTrade.rows)-1):
			ret += BtaxTrade.rows[i] + ','
		return ret + BtaxTrade.rows[len(BtaxTrade.rows)-1]


	def __init__(self, date, action, symbol, volume, currency, price, fee, feeCurrency): 
		self.date = date
		self.action = action
		self.symbol = symbol
		self.volume = volume
		self.currency = currency
		self.price = price	# Will leave blank for lookup
		self.fee = fee
		self.feeCurrency = feeCurrency 	# Will ignore in .csv output

	def __str__(self): 
		return str(self.date + ',' + self.action + ',' + self.symbol + ',' + self.volume + ',' + self.currency +
				   ',' + self.price + ',' + self.fee + ',' + self.feeCurrency)


class GdaxTrade: 

	rows = ['TIMESTAMP', 'ACCOUNT NAME', 'TYPE', 'BALANCE', 'AMOUNT', 'CURRENCY', 'EQUIV USD', 'ID']

	def __init__(self, timestamp, accountName, type, balance, amount, currency, equivUsd, id):
		self.timestamp = timestamp
		self.accountName = accountName
		self.type = type
		self.balance = balance
		self.amount = amount
		self.currency = currency
		self.equivUsd = equivUsd
		self.id = id

	def __str__(self):
		return str(self.timestamp + ',' + self.accountName + ',' + self.type + ',' + self.balance + ',' 
			   + self.amount + ',' + self.currency + ',' + self.equivUsd + ',' + self.id)


# Imports
import csv # for DictReader
import sys # for sys.exit()

# Defines
# inFilename = 'GDAXhistoryForBitcoinTax.txt'
inFilename = '/Users/mattpopovich/Documents/Coinbase/GDAXhistoryForBitcoinTax.txt'
outFilename = '/Users/mattpopovich/Documents/Coinbase/BitcoinTax.txt'
outFile = open(outFilename, 'w')
finalTrades = []
tradeCounter = 0 
rowCounter = 1

# Main program
# print BtaxTrade.header()
outFile.write(BtaxTrade.header() + '\n')

with open(inFilename, 'rb') as csvfile: 
	# spamreader = csv.reader(csvfile, delimiter=',')
	spamreader = csv.DictReader(csvfile)
	for row in spamreader: 
		rowOne = GdaxTrade(row[GdaxTrade.rows[0]], row[GdaxTrade.rows[1]], row[GdaxTrade.rows[2]], row[GdaxTrade.rows[3]], 
						   row[GdaxTrade.rows[4]], row[GdaxTrade.rows[5]], row[GdaxTrade.rows[6]], row[GdaxTrade.rows[7]])
		fee = '0' 

		if(row['TYPE'] == 'transfer'):
			rowCounter += 1 
			# print "rowCounter: " + str(rowCounter)
			continue # Skip this row 

		# If there was a fee applicable in the trade, the order of rows will be: 
		#		rowOne 		USD 	fee
		#		rowTwo		USD 	match
		#		rowThree	BTC 	match
		if(row['TYPE'] == 'fee'): 
			fee = str(abs(float(row['AMOUNT'])))
			if(row['CURRENCY'] != 'USD'): 
				sys.exit("Fee was in something other than USD!")

			row = next(spamreader)
			usdTrade = GdaxTrade(row[GdaxTrade.rows[0]], row[GdaxTrade.rows[1]], row[GdaxTrade.rows[2]], 
								 row[GdaxTrade.rows[3]], row[GdaxTrade.rows[4]], row[GdaxTrade.rows[5]],
								 row[GdaxTrade.rows[6]], row[GdaxTrade.rows[7]])
			row = next(spamreader)
			btcTrade = GdaxTrade(row[GdaxTrade.rows[0]], row[GdaxTrade.rows[1]], row[GdaxTrade.rows[2]], 
								 row[GdaxTrade.rows[3]], row[GdaxTrade.rows[4]], row[GdaxTrade.rows[5]],
								 row[GdaxTrade.rows[6]], row[GdaxTrade.rows[7]])

			# print rowOne
			# print usdTrade
			# print btcTrade
			rowCounter += 3 
		else: 
			usdTrade = rowOne
			row = next(spamreader)
			btcTrade = GdaxTrade(row[GdaxTrade.rows[0]], row[GdaxTrade.rows[1]], row[GdaxTrade.rows[2]], 
								 row[GdaxTrade.rows[3]], row[GdaxTrade.rows[4]], row[GdaxTrade.rows[5]],
								 row[GdaxTrade.rows[6]], row[GdaxTrade.rows[7]])
			# print usdTrade
			# print btcTrade
			rowCounter += 2 


		# print "tradeCounter: " + str(tradeCounter) 
		tradeCounter += 1 

		# print "rowCounter: " + str(rowCounter)

		action = 'SELL' if float(usdTrade.amount) > 0 else 'BUY'
		volume = str(abs(float(btcTrade.amount)))
		price = str(abs(float(btcTrade.equivUsd)) / abs(float(btcTrade.amount)))

		newTrade = BtaxTrade(usdTrade.timestamp, action, 'Online', btcTrade.currency, volume, price, usdTrade.currency, fee)
		# print newTrade
		outFile.write(str(newTrade) + '\n')
		finalTrades.append(newTrade)




















