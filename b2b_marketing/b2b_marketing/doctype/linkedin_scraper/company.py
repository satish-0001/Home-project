import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Scraper
from .person import Person
import time
import os

class CompanySummary(object):
    linkedin_url = None
    name = None
    followers = None

    def __init__(self, linkedin_url = None, name = None, followers = None):
        self.linkedin_url = linkedin_url
        self.name = name
        self.followers = followers

    def __repr__(self):
        if self.followers == None:
            return """ {name} """.format(name = self.name)
        else:
            return """ {name} {followers} """.format(name = self.name, followers = self.followers)

class Company(Scraper):
    linkedin_url = None
    name = None
    about_us =None
    website = None
    headquarters = None
    founded = None
    company_type = None
    company_size = None
    specialties = None
    showcase_pages =[]
    affiliated_companies = []
    def __init__(self, linkedin_url = None, name = None, about_us =None, website = None, headquarters = None, founded = None, company_type = None, company_size = None, specialties = None, showcase_pages =[], affiliated_companies = [], driver = None, scrape = True, get_employees = True, close_on_complete = True):
        print("ooooooopppppppppp2222221")
        self.linkedin_url = linkedin_url
        self.name = name
        self.about_us = about_us
        self.website = website
        self.headquarters = headquarters
        self.founded = founded
        self.company_type = company_type
        self.company_size = company_size
        self.specialties = specialties
        self.showcase_pages = showcase_pages
        self.affiliated_companies = affiliated_companies

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(os.path.dirname(__file__), 'drivers/chromedriver')
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        driver.get(linkedin_url)
        self.driver = driver
        print("999000000000000000000",self.driver,driver)
        if scrape:
            self.scrape(get_employees=get_employees, close_on_complete=close_on_complete)

    def __get_text_under_subtitle(self, elem):
        return "\n".join(elem.text.split("\n")[1:])

    def __get_text_under_subtitle_by_class(self, driver, class_name):
        return self.__get_text_under_subtitle(driver.find_element(By.CLASS_NAME,class_name))
        

    def scrape(self, get_employees = True, close_on_complete = True):
        if self.is_signed_in():
            self.scrape_logged_in(get_employees = get_employees, close_on_complete = close_on_complete)
        else:
            self.scrape_not_logged_in(get_employees = get_employees, close_on_complete = close_on_complete)

    def __parse_employee__(self, employee_raw):
        try:
            return Person(
                linkedin_url = employee_raw.find_element(By.CLASS_NAME,"search-result__result-link").get_attribute("href"),
                name = employee_raw.find_element(By.CLASS_NAME,"search-result__result-link")[1].text.strip(),
                driver = self.driver,
                get = False,
                scrape = False
                )
        except:
            return None

    def get_employees(self, wait_time=10):
        list_css = "search-results"
        next_xpath = '//button[@aria-label="Next"]'
        driver = self.driver

        see_all_employees = driver.find_element(By.XPATH,'//a[@data-control-name="topcard_see_all_employees"]')
        driver.get(see_all_employees.get_attribute("href"))

        _ = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, list_css)))

        total = []
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")
        results_list = driver.find_element(By.CLASS_NAME,list_css)
        results_li = results_list.find_element(By.TAG_NAME,"li")
        for res in results_li:
            total.append(self.__parse_employee__(res))

        while self.__find_element_by_xpath__(next_xpath):
            driver.find_element_(By.XPATH,next_xpath).click()
            _ = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, list_css)))

            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/4));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/3));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*2/3));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")

            results_list = driver.find_element(By.CLASS_NAME,list_css)
            results_li = results_list.find_element(By.TAG_NAME,"li")
            for res in results_li:
                _ = WebDriverWait(driver, wait_time).until(EC.visibility_of(res))
                total.append(self.__parse_employee__(res))



    def scrape_logged_in(self, get_employees = True, close_on_complete = True):
        driver = self.driver

        driver.get(self.linkedin_url)

        _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'nav-main__content')))
        _ = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@dir="ltr"]')))

        navigation = driver.find_element(By.CLASS_NAME,"org-page-navigation__items ")

        self.name = driver.find_element(By.XPATH,'//span[@dir="ltr"]').text.strip()
        navigation.find_elements_by_xpath("//a[@data-control-name='page_member_main_nav_about_tab']")[0].click()

        _ = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'section')))
        time.sleep(3)

        grid = driver.find_element(By.TAG_NAME,"section")[3]
        self.about_us = grid.find_element(By.TAG_NAME,"p")[0].text.strip()

        values = grid.find_element(By.TAG_NAME,"dd")
        self.specialties = "\n".join(values[-1].text.strip().split(", "))
        self.website = values[0].text.strip()
        self.headquarters = values[5].text.strip()
        self.industry = values[2].text.strip()
        self.company_size = values[3].text.strip()

        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")


        try:
            _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'company-list')))
            showcase, affiliated = driver.ffind_element(By.CLASS_NAME,"company-list")
            driver.find_element(By.ID,"org-related-companies-module__show-more-btn").click()

            # get showcase
            for showcase_company in showcase.find_element(By.CLASS_NAME,"org-company-card"):
                companySummary = CompanySummary(
                        linkedin_url = showcase_company.find_element(By.CLASS_NAME,"company-name-link").get_attribute("href"),
                        name = showcase_company.find_element(By.CLASS_NAME,"company-name-link").text.strip(),
                        followers = showcase_company.find_element(By.CLASS_NAME,"company-followers-count").text.strip()
                    )
                self.showcase_pages.append(companySummary)

            # affiliated company

            for affiliated_company in showcase.find_element(By.CLASS_NAME,"org-company-card"):
                companySummary = CompanySummary(
                         linkedin_url = affiliated_company.find_element(By.CLASS_NAME,"company-name-link").get_attribute("href"),
                        name = affiliated_company.find_element(By.CLASS_NAME,"company-name-link").text.strip(),
                        followers = affiliated_company.find_element(By.CLASS_NAME,"company-followers-count").text.strip()
                        )
                self.affiliated_companies.append(companySummary)

        except:
            pass

        if get_employees:
            self.get_employees()

        driver.get(self.linkedin_url)

        if close_on_complete:
            driver.close()

    def scrape_not_logged_in(self, close_on_complete = True, retry_limit = 10, get_employees = True):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            page = driver.get(self.linkedin_url)
            retry_times = retry_times + 1

        self.name = driver.find_element(By.CLASS_NAME,"name").text.strip()

        self.about_us = driver.find_element(By.CLASS_NAME,"basic-info-description").text.strip()
        self.specialties = self.__get_text_under_subtitle_by_class(driver, "specialties")
        self.website = self.__get_text_under_subtitle_by_class(driver, "website")
        self.headquarters = driver.find_element(By.CLASS_NAME,"adr").text.strip()
        self.industry = driver.find_element(By.CLASS_NAME,"industry").text.strip()
        self.company_size = driver.find_element(By.CLASS_NAME,"company-size").text.strip()
        self.company_type = self.__get_text_under_subtitle_by_class(driver, "type")
        self.founded = self.__get_text_under_subtitle_by_class(driver, "founded")

        # get showcase
        try:
            driver.find_element(By.ID,"view-other-showcase-pages-dialog").click()
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'dialog')))

            showcase_pages = driver.find_element(By.CLASS_NAME,"company-showcase-pages")[1]
            for showcase_company in showcase_pages.find_element(By.TAG_NAME,"li"):
                name_elem = showcase_company.find_element(By.CLASS_NAME,"name")
                companySummary = CompanySummary(
                    linkedin_url = name_elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    name = name_elem.text.strip(),
                    followers = showcase_company.text.strip().split("\n")[1]
                )
                self.showcase_pages.append(companySummary)
            driver.find_element(By.CLASS_NAME,"dialog-close").click()
        except:
            pass

        # affiliated company
        try:
            affiliated_pages = driver.find_element(By.CLASS_NAME,"affiliated-companies")
            for i, affiliated_page in enumerate(affiliated_pages.find_element(By.CLASS_NAME,"affiliated-company-name")):
                if i % 3 == 0:
                    affiliated_pages.find_element(By.CLASS_NAME,"carousel-control-next").click()

                companySummary = CompanySummary(
                    linkedin_url = affiliated_page.find_element(By.TAG_NAME,"a").get_attribute("href"),
                    name = affiliated_page.text.strip()
                )
                self.affiliated_companies.append(companySummary)
        except:
            pass

        if get_employees:
            self.get_employees()

        driver.get(self.linkedin_url)

        if close_on_complete:
            driver.close()

    def __repr__(self):
        return """
{name}

{about_us}

Specialties: {specialties}

Website: {website}
Industry: {industry}
Type: {company_type}
Headquarters: {headquarters}
Company Size: {company_size}
Founded: {founded}

Showcase Pages
{showcase_pages}

Affiliated Companies
{affiliated_companies}
    """.format(
        name = self.name,
        about_us = self.about_us,
        specialties = self.specialties,
        website= self.website,
        industry= self.industry,
        company_type= self.company_type,
        headquarters= self.headquarters,
        company_size= self.company_size,
        founded= self.founded,
        showcase_pages = self.showcase_pages,
        affiliated_companies = self.affiliated_companies
    )
