from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import json
import time
from bs4 import BeautifulSoup as BSoup


start_time = time.time()

def create_driver():
    driver_path = "/home/louis/Desktop/drivers/geckodriver"
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.add_argument("--headless")
    return webdriver.Firefox(executable_path=driver_path, options=firefoxOptions)


driver = create_driver()
driver.get("https://www.immoweb.be/fr/recherche/maison-et-appartement/a-vendre?countries=BE")
cookie_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='uc-btn-accept-banner']")))
cookie_button.click()

first_listing = driver.find_element(By.XPATH,"//li[@class='search-results__item']")
first_listing.click()


def get_houses():

    houses_list = []
    bs_obj = BSoup(driver.page_source, 'html.parser')
    for j in range (0,10):
        find_all_ths = bs_obj.find_all('th')
        ths = []
        for th in find_all_ths:
            ths.append(re.sub('\s\s+', '', th.get_text()))
        tds = []
        find_all_tds = bs_obj.find_all('td')
        for td in find_all_tds:
            tds.append(re.sub('\s\s+', '', td.get_text()))
        
        house_id = re.sub('\s\s+', '', bs_obj.find_all('div',{"class":"classified__header--immoweb-code"})[1].get_text())
        try: 
            post_code = re.sub('\s\s+', '', bs_obj.find_all('span',{"class":"classified__information--address-row"})[1].get_text())
        except NoSuchElementException:
            post_code = re.sub('\s\s+', '', bs_obj.find_all('span',{"class":"classified__information--address-row"})[0].get_text())
        type_of_property = re.sub('\s\s+', '', bs_obj.find_all('h1',{"class":"classified__title"})[0].get_text())
        
        type_of_sale = re.sub('\s\s+', '', bs_obj.find_all('span',{"class":"flag-list__text"})[1].get_text())
        

        list3 = []

        for i in range(len(ths)):
            list3.append([ths[i],tds[i]])
        list3.insert(0,["id",house_id])
        list3.insert(0,["locality",post_code])
        list3.insert(0,["type of property",type_of_property])
        list3.insert(0,["type of sale",type_of_sale])

        dict1 = dict(list3)
        houses_list.append(dict1)
        next_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[1]/div[2]/div/div/div[1]/div/div[1]/ul/li[2]/a/span[2]")
        print(f'loop {j} executed')
        next_button.click()
        j += 1

    driver.close()
    return houses_list

all_houses = get_houses()

print("--- %s seconds ---" % (time.time() - start_time))
df = pd.DataFrame(all_houses) 

# df = pd.DataFrame.from_dict({(i,j): houses_dict[i][j] 
#                            for i in houses_dict.keys() 
#                            for j in houses_dict[i].keys()},
#                        orient='index')

df.to_csv('houses_infos_test.csv') 

# # pd.read_csv('houses_infos.csv', header=None).T.to_csv('output.csv', header=False, index=False)

out_file = open("houses_dict.json", "w")  
json.dump(all_houses, out_file, default=lambda o: '<not serializable>', indent = 4)
out_file.close()