from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
from pprint import pprint
import json

client = MongoClient('localhost', 27017)
db = client['mvideo']
purchase = db.purchase

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')

time.sleep(2)
# На случай всплывающего окна при загрузке сайта
while True:
    try:
        button = driver.find_element_by_xpath("//span[@class='c-btn_close font-icon icon-delete']")
        button.click()
        break
    except Exception as e:
        break

time.sleep(4)
purchases = []

button = driver.find_element_by_xpath("//ul[contains(@data-init-param, 'Новинки')]")
actions = ActionChains(driver)
actions.move_to_element(button)
actions.perform()
time.sleep(2)

a = 0
while True:
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//div[@data-holder='#loadSubMultiGalleryblock5260654']//a[@class='next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right']"))
        )
        new_things = driver.find_elements_by_xpath("//ul[contains(@data-init-param, 'Новинки')]/li")
        if len(new_things) > a:
            a = len(new_things)
            print(len(new_things))
            for thing in new_things:
                purch = thing.find_element_by_tag_name('a').get_attribute('data-product-info')
                current_purchase = json.loads(purch)
                current_purchase['_id'] = current_purchase.pop('productId')
                pprint(current_purchase)
                purchase.update_one({'_id': current_purchase['_id']}, {'$set': current_purchase}, upsert=True)
            button.click()
            time.sleep(3)
            continue

        if len(new_things) == a:
            break


    except Exception as e:
        print(e)
        continue
