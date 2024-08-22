import getpass
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def __prompt_email_password():
  u = input("Email: ")
  p = getpass.getpass(prompt="Password: ")
  return (u, p)

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

def login(driver, email=None, password=None):
  if not email or not password:
    email, password = __prompt_email_password()

  driver.get("https://www.linkedin.com/login")
  element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
  email_elem = driver.find_element(By.ID,"username")
  email_elem.send_keys(email)

  password_elem = driver.find_element(By.ID,"password")
  password_elem.send_keys(password)
  driver.find_element(By.TAG_NAME,"button").click()
  element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "ember29")))
  print("9999999999999999999333",element)