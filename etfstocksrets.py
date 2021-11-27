import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
from lxml import etree
from lxml import html
from urllib.request import urlopen, Request
from selenium import webdriver
from selenium import *
from selenium.webdriver.common.keys import Keys
import matplotlib.pyplot as plt



def main():
	url = 'https://seekingalpha.com/etfs-and-funds/etf-tables/themes_and_subsectors'
	driver = webdriver.Chrome(r'C:\Users\<>\chromedriver.exe')

	driver.get(url)
	driver.minimize_window()

	time.sleep(1)

	etfs = driver.find_elements_by_class_name('data_lists_pages_cont_and_ads')
	etfs_names = driver.find_elements_by_class_name('eft_or_etn')
		
	etfs_names = [x.text for x in etfs_names]

	etfs_names_clean = [x for x in etfs_names if 'ETF or ETN' not in x]

	etf_symbols = []
	for index, value in enumerate(etfs_names_clean):
		print(f'{index}: {" ".join([i for i in value.split(" ") if i != value.split(" ")[-1]])}, Symbol: {value.split(" ")[-1]}')
		etf_symbols.append(value.split(" ")[-1])

	etf_symbols = [str(i).lower() for i in etf_symbols]

	answer = str(input("Select ETF for which you want to see the relative strength of its holdings: ")).lower()
	while answer not in etf_symbols:
		answer = input("Select ETF for which you want to see the relative strength of its holdings: ").lower()
	if answer in etf_symbols:
		VisualizeData(scrape_stocks(answer))

def scrape_stocks(ETF):
	url = 'https://www.marketwatch.com/investing/fund/{}/holdings?mod=mw_quote_tab'.format(ETF)

	dfs = pd.read_html(url)
	perfData = dfs[6].drop(dfs[6].columns[[0,-1]], axis = 1)

	AllData = pd.DataFrame()
	
	for i,ticker in enumerate(perfData['Symbol']):
		
		req = Request(url='https://finviz.com/quote.ashx?t={}'.format(ticker),headers={'user-agent':'my-app'})
		try:
			response = urlopen(req)

		except:
			continue
		print(ticker)
		html = BeautifulSoup(response, 'html')
		info_table = html.find_all(class_= "snapshot-table2")
		
		info_tables = dict()

		info_tables[ticker] = info_table

		ticker_data = info_tables[ticker]

		ticker_rows = [result.findAll('tr') for result in ticker_data]
		ticker_rows_content = [result.findAll('b') for result in ticker_data]

		numbers = [item.text for item in ticker_rows_content[0]]
		numbers = [item.replace('%','') if '%' in item else item for item in numbers]

		data = {}

		x = 0
		for index,row in enumerate(ticker_rows[0]):


			onlyString = ''.join([item for item in row.text if not item.isdigit()])


			cleanOnlyString = onlyString.split("\n")[1:-1]
			cleanOnlyString = [i.replace('%','') if '%' in i else i for i in cleanOnlyString]
			cleanOnlyString = [i.replace('.','') if '.' in i else i for i in cleanOnlyString]
			cleanOnlyString = [i.replace('-','') if '-' in i else i for i in cleanOnlyString]

			count = 0

			for i2,value in enumerate(cleanOnlyString):
				
				count += 1

				data[value] = numbers[x]
				x += 1

				if count== 6:
					break

		AllData[ticker] = [data['Perf Month'],data['Perf Year']]
	return(AllData)

def VisualizeData(df):
	df = pd.DataFrame(df.T)
	df = df.rename(columns={0:'1 Month Returns', 1:'1 Year Returns'})

	df = df.drop(df[df['1 Year Returns'] == '-'].index)

	df[['1 Month Returns','1 Year Returns']] = df[['1 Month Returns','1 Year Returns']].astype(float)
	
	fig, ax = plt.subplots(figsize=(10,6))
	ax.scatter(x = df['1 Year Returns'], y = df['1 Month Returns'])
	plt.ylim(min(df['1 Month Returns']), max(df['1 Month Returns']))

	plt.xlabel('1 Year Returns (%)')
	plt.ylabel('4 Week Returns (%)')

	for i, txt in enumerate(df.index):
		ax.annotate(txt, (df['1 Year Returns'][i], df['1 Month Returns'][i]))

	plt.show()

	answer = str(input("Would you like to analyze leadership of other ETF data?: ")).lower().strip()

	while answer not in ('y','yes','n','no'):
		answer = str(input("Would you like to analyze leadership of other ETF data?: ")).lower().strip()
	if answer in ('y','yes'):
		main()
	elif answer in ('n','no'):
		exit()

main()
