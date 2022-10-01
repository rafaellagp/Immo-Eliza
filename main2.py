from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import time
from bs4 import BeautifulSoup as BSoup
import os
import pickle
# import multiprocessing as mp
# from threading import Thread, RLock

start_time = time.time()

search_url_house = "https://www.immoweb.be/en/search/house/for-sale?countries=BE&isALifeAnnuitySale=false&page="
search_url_apartment = "https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page="
search_url_list = [search_url_house,search_url_apartment]

def create_driver():
    driver_path = "/home/antoine/VS Code Projects/BXL-Bouman-5-Antoine/content/0.projects/2.immo_eliza/geckodriver"
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = True

    return webdriver.Firefox(executable_path=driver_path, options=firefoxOptions)

def doesFileExists(filePathAndName):
    return os.path.exists(filePathAndName)

driver = create_driver()

def split_url(url):
    split_url = re.split('/|\?', url)
    return split_url

def get_all_urls(number_of_urls):

    # if doesFileExists('url_list.ob'):
    #     with open ('url_list.ob', 'rb') as fp:
    #         url_list = pickle.load(fp)
    if doesFileExists('id_list.ob'):
        with open ('id_list.ob', 'rb') as fp:
            id_list = pickle.load(fp)
    else:
        # url_list = []
        id_list = []
    
    for url in search_url_list:
        driver.get(url)
        try:
            cookie_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='uc-btn-accept-banner']")))
            cookie_button.click()
        except:
            pass
        page_index = 1
        while len(set(id_list))<number_of_urls and page_index<=180:
            driver.get(url + str(page_index))

            bs_obj = BSoup(driver.page_source, 'html.parser')
            for a in bs_obj.find_all('a', attrs={"class" : "card__title-link"}):
                if split_url(a['href'])[9] not in list(set(id_list)):
                    # url_list.append(a['href'])
                    id_list.append(split_url(a['href'])[9])
                    # with open('url_list.ob', 'wb') as fp:
                    #     pickle.dump(url_list, fp)
                    with open('id_list.ob', 'wb') as fp:
                        pickle.dump(id_list, fp)
            print("page= ", page_index)
            print(len(id_list))
            # print(len(url_list))
            print(len(set(id_list)))
            # print(len(set(url_list)))
            page_index +=1
    
    return id_list

def get_house_info(number_of_entries):

    id_list = get_all_urls(number_of_entries)
    print("id list length= ",len(id_list))
    print("id list cleaned= ",len(set(id_list)))

    
    if not doesFileExists("test.csv"):
        pd.DataFrame({}).to_csv("test.csv")
    
    output = pd.read_csv("test.csv")

    with open('test.csv', 'r') as fp:
        s = fp.read()

    new_listing_count = 0
    for id in list(set(id_list)):
        # print("id= ",id)

        if id not in s:
            driver.get("https://www.immoweb.be/en/classified/"+id)
            current_url = driver.current_url
            list_from_url = split_url(current_url)

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

            house_list.insert(0,["id",id])
            house_list.insert(0,["locality",locality])
            house_list.insert(0,["post code",post_code])
            house_list.insert(0,["type of property",type_of_property])
            house_list.insert(0,["type of sale",type_of_sale])

            house_dict = dict(house_list)
            keys = list(house_dict.keys())

            df_dictionary = pd.DataFrame([house_dict])
            output = pd.concat([output, df_dictionary],ignore_index=True)
            output.to_csv("test.csv", index=False)
            new_listing_count +=1
            print("new listings added: ", new_listing_count)
        id_list_set = list(set(id_list))
        print(id_list_set.index(id)+1,"/",len(id_list_set))


    
    return

# get_house_info(200)
get_all_urls(10500)

print("--- %s seconds ---" % (time.time() - start_time))
