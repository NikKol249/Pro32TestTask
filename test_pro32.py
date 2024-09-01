#from seleniumwire import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
import configparser
import time as t
import pickle
import random
import string

@pytest.fixture()
def parsConfigFile():
    config = configparser.RawConfigParser()
    config.read('config.cfg')    
    details_dict = dict(config.items('config'))
    print(details_dict.get('login_page'))
    return details_dict

@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    yield driver
    driver.close()
    driver.quit()
    
# Генерация случайных строк и сохранение их в качестве имени и фамилии для будущего использования
def random_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))
fn = random_string()
sn = random_string()

# Сохранение cookie-данных для последующих запросов
def save_cookie(cookies, path):
    with open(path, "wb") as file:
        pickle.dump(cookies, file)

# Загрузка cookie-данных в драйвер
def load_cookie(driver, path):
    with open(path, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)


def test_login(driver, parsConfigFile):
    driver.get(parsConfigFile.get('login_page'))

    email_input = driver.find_element(By.ID, 'email')
    email_input.clear()
    email_input.send_keys(parsConfigFile.get('login'))

    button_next = driver.find_element(By.XPATH, '//button')
    button_next.click()

    password_input = driver.find_element(By.XPATH, '//input[@id="password"]')
    password_input.clear()
    password_input.send_keys(parsConfigFile.get('password'))

    button_sign_in = driver.find_element(By.CSS_SELECTOR, '.js-form-right > div.form__actions > div > button') 
    button_sign_in.click()
    t.sleep(2) # ожидание полной загрузки страницы перед сохранением cookie
    
    save_cookie(driver.get_cookies(), "cookies.pkl")


def test_change_account_data(driver):
    driver.get('https://getscreen.dev/panel/account/profile')

    load_cookie(driver, "cookies.pkl") # подгрузка cookie
    response = driver.get('https://getscreen.dev/panel/account/profile')

    input_name = driver.find_element(By.XPATH, '//input[@data-test-id="page-profile-name"]')
    input_name.send_keys(Keys.CONTROL, 'a')
    input_name.send_keys(Keys.BACKSPACE)
    
    input_name.send_keys(fn)

    input_surname = driver.find_element(By.XPATH, '//input[@data-test-id="page-profile-surname"]')
    input_surname.send_keys(Keys.CONTROL, 'a')
    input_surname.send_keys(Keys.BACKSPACE)

    input_surname.send_keys(sn)

    button_save = driver.find_element(By.XPATH, '//button[@data-test-id="page-profile-update"]')
    button_save.click()

    t.sleep(1)

def test_change_check(driver):
    driver.get('https://getscreen.dev/panel/account/profile')

    load_cookie(driver, "cookies.pkl") # подгрузка cookie
    response = driver.get('https://getscreen.dev/panel/account/profile')

    input_name = driver.find_element(By.XPATH, '//input[@data-test-id="page-profile-name"]')
    assert input_name.get_attribute("value") == fn
    
    input_surname = driver.find_element(By.XPATH, '//input[@data-test-id="page-profile-surname"]')
    assert input_surname.get_attribute("value") == sn