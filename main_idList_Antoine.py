from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import time
from bs4 import BeautifulSoup as BSoup
import os
import pickle
import multiprocessing as mp
import requests
import json

number_of_entries = 10

start_time = time.time()

# house and apartments search pages split with both the life-annuity-sale set to false
search_url_house = "https://www.immoweb.be/en/search/house/for-sale?countries=BE&isALifeAnnuitySale=false&page="
search_url_apartment = "https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page="
search_url_list = [search_url_house,search_url_apartment]

def create_driver():
    
    ''' Creates the web driver necessary to open the browser and scrape the pages content'''

    driver_path = "/home/antoine/VS Code Projects/BXL-Bouman-5-Antoine/content/0.projects/2.immo_eliza/geckodriver"
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = True

    return webdriver.Firefox(executable_path=driver_path, options=firefoxOptions)

def doesFileExists(filePathAndName):

    ''' Checks if a file we want to open and/or write to already exists'''

    return os.path.exists(filePathAndName)

def split_url(url):

    '''Splits an url by the "/" and "?" characters in order to get infos from a listing straight from its url'''

    split_url = re.split('/|\?', url)
    return split_url

def get_all_ids(number_of_ids):

    '''Function to retrieve all the url's and id's of listings from the search pages. 
    Better to use the id though, to make sure it's unique and not get any duplicates in the dataframe later on.
    Also made to update an existing .ob file or create a new one if not'''

    if doesFileExists('id_list.ob'):
        with open ('id_list.ob', 'rb') as fp:
            id_list = pickle.load(fp)
    else:
        id_list = []
    
    driver = create_driver()
    for url in search_url_list:
        driver.get(url)
        try:
            cookie_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='uc-btn-accept-banner']"))) 
            cookie_button.click() # waits for the cookie prompt to appear and click on the accept button
        except:
            pass # or pass if there's none

        page_index = 1
        number_of_id_init = len(set(id_list))
        while len(set(id_list))<number_of_ids and page_index<=180:  
        # page index limit cause it can't go further than 333 on immoweb. 
        # We split here the search pages in 2 to get enough id's and to have +/- same amount of houses and apartments
            if len(set(id_list)) - number_of_id_init > number_of_ids:
                break

            driver.get(url + str(page_index))
            bs_obj = BSoup(driver.page_source, 'html.parser')

            for a in bs_obj.find_all('a', attrs={"class" : "card__title-link"}):
                if split_url(a['href'])[9] not in list(set(id_list)):
                    id_list.append(split_url(a['href'])[9])
                    with open('id_list.ob', 'wb') as fp:
                        pickle.dump(id_list, fp)

            print("page= ", page_index)
            print("id list length= ",len(id_list))
            page_index +=1
    
    return id_list

def house_scraping(id):

    driver = create_driver()

    driver.get("https://www.immoweb.be/en/classified/"+id)
    
    current_url = driver.current_url
    list_from_url = split_url(current_url)
    post_code = list_from_url[8]
    locality = list_from_url[7]
    type_of_property = ' '.join(list_from_url[5].split('-'))
    bs_obj = BSoup(driver.page_source, 'html.parser')
    # try:
    #     # type_of_sale = bs_obj.find("span",{ "class" : "flag-list__text"}).get_text()
    #     type_of_sale = driver.find_element(By.XPATH,"//div[@class='flag-list__item flag-list__item--secondary']//span[@class='flag-list__text']").text
    # except NoSuchElementException:
    #     type_of_sale = str()
    find_all_ths = bs_obj.find_all('th')
    ths = []
    for th in find_all_ths:
        ths.append(re.sub('\s\s+', '', th.get_text()))
    tds = []
    find_all_tds = bs_obj.find_all('td')
    for td in find_all_tds:
        tds.append(re.sub('\s\s+', '', td.get_text()))
            
    house_dict = dict(zip(ths,tds))

    house_dict["locality"] = locality
    house_dict["post code"] = post_code
    # house_dict["type of sale"] = type_of_sale
    house_dict["type of property"] = type_of_property
    house_dict["id"] = id
    print("it did something")

    return house_dict

def add_to_csv():
    output = pd.read_csv("test.csv")
    df_dictionary = pd.read_json("new_entries_dict.json") 
    output = pd.concat([output, df_dictionary],ignore_index=True) # global dataframe is updated by concatenating the new entry to the existing file
    output.to_csv("test.csv", index=False)



def get_houses_info(number_of_entries):
    
    if not doesFileExists("test.csv"):
        df = pd.DataFrame()
    else:    
        df = pd.read_csv("test.csv")

    id_list = set(get_all_ids(number_of_entries))
    print("ids list length= ",len(id_list))

    new_id_list = list(id_list - set(df["id"]))[:number_of_entries]
    print(new_id_list)
    print("new id list length= ",len(new_id_list))

    with mp.Pool() as pool:
        new_entries = list(pool.map(house_scraping, new_id_list))
        out_file = open("new_entries_dict.json", "w")
        json.dump(new_entries,out_file)
    
    add_to_csv()

get_houses_info(number_of_entries)
# get_all_ids(10500)

print("--- %s seconds ---" % (time.time() - start_time))
