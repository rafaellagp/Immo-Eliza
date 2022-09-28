from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


driver_path = "/home/louis/Desktop/drivers/geckodriver"
driver = webdriver.Firefox(executable_path=driver_path)

driver.get("https://www.immoweb.be/fr/recherche/maison-et-appartement/a-vendre?countries=BE")


cookie_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@id='uc-btn-accept-banner']")))
cookie_button.click()

number_of_houses_raw = driver.find_element(By.XPATH, "//span[@class='button__label-count']")
number_of_houses = re.sub(r"[\(\)\ ]",'',number_of_houses_raw.text)
print(type(number_of_houses))

first_house_link = driver.find_element(By.XPATH, "//a[@id='']")
first_house_link.click()
# installations = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[3]/div[7]/div/div/div/div/div[2]/table/tbody")
# installation_list = []
# for installation in installations:
#     installation_list.append(installations[installation].text)
# print(installation_list)
find_all_ths = driver.find_elements(By.XPATH, "//th[@class='classified-table__header']")
find_all_trs = driver.find_elements(By.XPATH, "//td[@class='classified-table__data']")
list3 = []
for i in range(len(find_all_ths)):
    list3.append([find_all_ths[i].text, find_all_trs[i].text])

print(list3)

houses = []
i = 0
while i < 2:
    house_attributes = []
    swimingpool = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[3]/div[7]/div/div/div/div/div[2]/table/tbody/tr[5]/td")))
    house_attributes.append(swimingpool.text)
    houses.append(house_attributes)
    next_link = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div/main/div[1]/div[2]/div/div/div[1]/div/div[1]/ul/li[2]/a/span[2]")
    next_link.click()
    i += 1
print(houses)