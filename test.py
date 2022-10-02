import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


URL = 'https://mail.google.com/'

driver = webdriver.Chrome('chromedriver.exe')
driver.get(url=URL)

id = driver.find_element_by_xpath('//*[@id="identifierId"]')
id.send_keys('kimjunghyun696')
# driver.close()