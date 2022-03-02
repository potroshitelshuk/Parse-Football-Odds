from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup as bs
import pandas as pd
from time import sleep
from tqdm import tqdm
from IPython.display import clear_output
from main.py import web

def wait_visibility_class_name(web, class_name, timeout=10):
		WebDriverWait(web, timeout).until(
			EC.visibility_of_element_located((By.CLASS_NAME, class_name)))


def return_coef(page_source):
	soup = bs(page_source)
	text = soup.find('span', class_='spc spc-nowrap').text
	if 'Opening odds:' in text:
		coef = text.split('Opening odds:')[-1]
		if 'Click' in coef:
			coef = coef.split('Click')[0]

		coef = coef.split(' ')[-1]

		if coef:
			return float(coef)
		else:
			return np.nan
			print('SMTH WITH COEF')
	else:
		return np.nan
		print('No phrase in text')



def return_coefs(href):
	web.get(href)
	wait_visibility_class_name(web, 'table-main.detail-odds.sortable')
	books = web.find_element_by_class_name('table-main.detail-odds.sortable')
	all_books = books.find_elements_by_class_name('lo.odd') + books.find_elements_by_class_name('lo.even')    
	coefs = []
	book_found = 0
	for book in all_books:
		name = book.find_element_by_class_name('name').text
		if name == 'bet365':
			els = book.find_elements_by_css_selector('td')
			for el in els:
				if 'right' in el.get_attribute('class'):
					action = ActionChains(web)  
					action.move_to_element(el).perform()
					sleep(0.2)
					page_source = web.page_source
					coefs.append(return_coef(page_source))
			book_found = 1
			break


	if not book_found:
		return []
		

	return coefs



def get_hrefs(league_link):
	hrefs = set()
	web.get(league_link)
	wait_visibility_class_name(web, 'table-main')
	table = web.find_element_by_class_name('table-main')
	for line in table.find_elements_by_class_name('name.table-participant'):
		subels = line.find_elements_by_css_selector('a')
		for el in subels:
			href = el.get_attribute('href')
			if 'https' in el.get_attribute('href') and 'inplay' not in el.get_attribute('href'):
				hrefs.add(href)

	return hrefs

def get_team_names():
	table = web.find_element_by_id('col-content')
	title = table.find_element_by_css_selector('h1').text
	team1, team2 = title.split(' - ')
	return team1, team2

def get_date():
	table = web.find_element_by_id('col-content')
	info = table.find_element_by_css_selector('p').text
	date, time = info.split(', ')[1:]
	return date, time

def get_result():
	if web.find_elements_by_class_name('result') != []:
		wait_visibility_class_name(web, 'result')
		text = web.find_element_by_class_name('result').text
		result = text.split(' ')[2]
		return result
	return ''

				
def parse_next_matches(hrefs):
	print('Parsing next matches...')
	for href in tqdm(hrefs):
		if href not in data.index:
			coefs = return_coefs(href)
			team1, team2 = get_team_names()
			date, time = get_date()
			datetime = pd.to_datetime(date + ' ' + time)
			if len(coefs) == 3:
				data.loc[href] = [datetime, team1,
								  team2, np.nan, coefs[0],
								 coefs[1], coefs[2]]
			elif len(coefs) > 0:
				print('Not enough odds in match: {0}'.format(href))
#             print(date, time)
#             print(team1, team2)
		data.to_excel('odds.xlsx')
			

def parse_history(link):
	hrefs = get_hrefs(link)
	print('Parsing history...')
	for href in tqdm(hrefs):
		if href in data.index and data.loc[href, 'score'] != np.nan:
			web.get(href)
			result = get_result()
			data.loc[href, 'score'] = result
			data.to_excel('odds.xlsx')
			
