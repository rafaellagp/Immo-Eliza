from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import json




chrome_driver_path = "/home/antoine/VS Code Projects/BXL-Bouman-5-Antoine/content/0.projects/2.immo_eliza/chromedriver"

page_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page=1"

driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get(page_url)
driver.maximize_window()

cookie_button = driver.find_element(By.XPATH, "//*[@id='uc-btn-accept-banner']")
cookie_button.click()

first_listing = driver.find_element(By.XPATH,"//li[@class='search-results__item']")
first_listing.click()

houses_list = []

for j in range (0,10):

    find_all_ths = driver.find_elements(By.XPATH, "//th[@class='classified-table__header']")
    find_all_trs = driver.find_elements(By.XPATH, "//td[@class='classified-table__data']")
    house_id = driver.find_element(By.XPATH,"//div[@class='classified__header--immoweb-code']")
    try:
        post_code = driver.find_element(By.XPATH,"//span[@class='classified__information--address-row'][2]")
    except NoSuchElementException:
        post_code = driver.find_element(By.XPATH,"//span[@class='classified__information--address-row']")
    type_of_property = driver.find_element(By.XPATH,"//h1[@class='classified__title']")
    try:
        type_of_sale = driver.find_element(By.XPATH,"//div[@class='flag-list__item flag-list__item--secondary']//span[@class='flag-list__text']")
    except NoSuchElementException:
        type_of_sale = driver.find_element(By.XPATH,"//div[@class='classified-medias__button-label']")

    list3 = []

    for i in range(len(find_all_ths)):
        list3.append([find_all_ths[i].text,find_all_trs[i].text])
    list3.insert(0,["id",house_id.text])
    list3.insert(0,["locality",post_code.text])
    list3.insert(0,["type of property",type_of_property.text])
    list3.insert(0,["type of sale",type_of_sale.text])

    dict1 = dict(list3)

    houses_list.append(dict1)
    next_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[1]/div[2]/div/div/div[1]/div/div[1]/ul/li[2]/a/span[2]")

    next_button.click()
    

driver.close()

df = pd.DataFrame(houses_list) 

# df = pd.DataFrame.from_dict({(i,j): houses_dict[i][j] 
#                            for i in houses_dict.keys() 
#                            for j in houses_dict[i].keys()},
#                        orient='index')

df.to_csv('houses_infos_test.csv') 

# # pd.read_csv('houses_infos.csv', header=None).T.to_csv('output.csv', header=False, index=False)

out_file = open("houses_dict.json", "w")  
json.dump(houses_list, out_file, default=lambda o: '<not serializable>', indent = 4)
out_file.close()