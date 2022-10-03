from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import time
from bs4 import BeautifulSoup as BSoup
# import multiprocessing as mp
import os
from threading import Thread, RLock

rlock = RLock()

def doesFileExists(filePathAndName):
    return os.path.exists(filePathAndName)


houses_url = "https://www.immoweb.be/en/search/house/for-sale?countries=BE"
apart_url = "https://www.immoweb.be/en/search/apartment/for-sale?countries=BE"
search1_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&propertySubtypes=BUNGALOW,CASTLE,COUNTRY_COTTAGE,APARTMENT_BLOCK,TOWN_HOUSE,VILLA,MANOR_HOUSE,GROUND_FLOOR,TRIPLEX,PENTHOUSE,KOT&page=1&orderBy=relevance"
search2_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&propertySubtypes=CHALET,FARMHOUSE,EXCEPTIONAL_PROPERTY,MIXED_USE_BUILDING,MANSION,OTHER_PROPERTY,PAVILION,DUPLEX,FLAT_STUDIO,LOFT,SERVICE_FLAT&page=1&orderBy=relevance"
url_list = [houses_url,apart_url,search1_url,search2_url]

start_time = time.time()

def create_driver():
    driver_path = "/home/antoine/VS Code Projects/BXL-Bouman-5-Antoine/content/0.projects/2.immo_eliza/geckodriver"
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = True

    return webdriver.Firefox(executable_path=driver_path, options=firefoxOptions)

driver = create_driver()

def go_to_first_listing():
    driver.get("https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE")
    try:
        cookie_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='uc-btn-accept-banner']")))
        cookie_button.click()
    except:
        pass
    first_listing = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/ul/li[1]/article/div[1]/h2/a")
    first_listing.click()

def split_url():
    url = driver.current_url
    split_url = re.split('/|\?', url)
    return split_url


def get_house_info():
    
    list_from_url = split_url()
    # print(list_from_url)
    house_id = list_from_url[9]
    
    if not doesFileExists("test_next.csv"):
        pd.DataFrame({}).to_csv("test_next.csv")
    
    output = pd.read_csv("test_next.csv")


    with open('test_next.csv', 'r') as fp:
        s = fp.read()
    if house_id not in s:
        post_code = list_from_url[8]
        locality = list_from_url[7]
        type_of_property = list_from_url[5]
        type_of_sale = ' '.join(list_from_url[5].split('-'))
        bs_obj = BSoup(driver.page_source, 'html.parser')        
        find_all_ths = bs_obj.find_all('th')
        ths = []
        for th in find_all_ths:
            ths.append(re.sub('\s\s+', '', th.get_text()))
        tds = []
        find_all_tds = bs_obj.find_all('td')
        for td in find_all_tds:
            tds.append(re.sub('\s\s+', '', td.get_text()))
                
        house_list = []

        for i in range(len(ths)):
            house_list.append([ths[i],tds[i]])

        house_list.insert(0,["id",house_id])
        house_list.insert(0,["locality",locality])
        house_list.insert(0,["post code",post_code])
        house_list.insert(0,["type of property",type_of_property])
        house_list.insert(0,["type of sale",type_of_sale])

        house_dict = dict(house_list)
        keys = list(house_dict.keys())


        df_dictionary = pd.DataFrame([house_dict])
        output = pd.concat([output, df_dictionary],ignore_index=True)
        output.to_csv("test_next.csv", index=False)

    next_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[1]/div[2]/div/div/div[1]/div/div[1]/ul/li[2]/a/span[2]").click()
    return

def scraping():

    go_to_first_listing()
    
    for i in range(10):
        get_house_info()
        print(f'house number {i} register at time: {"--- %s seconds ---" % (time.time() - start_time)}')
    driver.quit()

scraping()

print("--- %s seconds ---" % (time.time() - start_time))
