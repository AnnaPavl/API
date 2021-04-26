import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['mail']
letters = db.letters

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://mail.ru/')

login = driver.find_element_by_name('login')
login.send_keys('study.ai_172')
login.send_keys(Keys.ENTER)

time.sleep(2)

password = driver.find_element_by_name('password')
password.send_keys('NextPassword172')
password.send_keys(Keys.ENTER)
time.sleep(2)
num = driver.find_element_by_xpath(
    '//a[@class="nav__item js-shortcut nav__item_active nav__item_shortcut nav__item_expanded_true nav__item_child-level_0"]')
#узнаем количество писем в папке "Входящие"
total = num.get_attribute('title').split(' ')[1]
total = int(total)
links = []

while len(links) != total:
    time.sleep(2)
    inbox = driver.find_elements_by_xpath(
        "//a[contains(@class,'llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal')]")
    for letter in inbox:
        link = letter.get_attribute('href')
        if link not in links:
            links.append(link)
    actions = ActionChains(driver)
    actions.move_to_element(inbox[-1])
    inbox[-1].send_keys(Keys.PAGE_DOWN)
    actions.perform()
    inbox = driver.find_elements_by_xpath('//a[@tabindex="-1"]')

for link in links:
    driver.get(link)
    time.sleep(2)
    current_letter = {}
    sender = driver.find_element_by_class_name('letter-contact').get_attribute('title')
    date = driver.find_element_by_class_name('letter__date').text
    theme = driver.find_element_by_tag_name('h2').text
    text = driver.find_element_by_class_name('letter__body').text
    id = link.split(':')[2]
    current_letter['sender'] = sender
    current_letter['date'] = date
    current_letter['theme'] = theme
    current_letter['text'] = text
    current_letter['_id'] = id
    letters.update_one({'_id': current_letter['_id']}, {'$set': current_letter}, upsert=True)
