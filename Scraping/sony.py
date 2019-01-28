from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
import time
import csv

def wait_for_load(driver, delay, frequency, element):
    retries = 0
    while(retries<5):
        try:
            myElem = WebDriverWait(driver, delay, poll_frequency = frequency).until(
                                   EC.presence_of_element_located((By.ID, element)))
            print("Page is ready!")
            return
        except TimeoutException:
            print("Loading took too much time!")
            retries+=1


if __name__ == '__main__':
    driver = webdriver.Firefox()
    delay = 5 #seconds
    frequency = 3 #check for element 3 times/delay
    driver.get("https://www.sony.co.in/electronics/tv/t/televisions")

    wait_for_load(driver, delay, frequency, 'gallery_tab_televisions_televisions-gallery-detailed')

    urls = [element.get_attribute('href') for element in driver.find_elements_by_xpath("//a[@class='product-link-to-pdp product-url']")]

    all_data = []
    for link in urls:
        driver.get(link + "/specifications")
        wait_for_load(driver, delay, frequency, 'page-main-content')
        try:
            detail_columns = driver.find_elements_by_xpath("//*[starts-with(@data-tab, 'spec-tab')]")
            col_num = 0
            for column in detail_columns:
                tv_data = {}
                # Using the detail_column xpath//spec cell xpaths here to help speed up script times.
                detail_column_str = "//div[@data-tab='spec-tab" + str(col_num) + "']"
                specs_cells = column.find_elements_by_xpath(detail_column_str + "//*[starts-with(@class, 'spec-item-cell')]")

                for spec in specs_cells:
                    heading = spec.find_element_by_tag_name("p").get_attribute("textContent")
                    details = spec.find_elements_by_tag_name("li")
                    tv_data[heading] = " ".join([det.get_attribute('textContent') for det in details])
                    print("*****"+heading+"*****")
                    print(" ".join([det.get_attribute('textContent') for det in details]))

                all_data.append(tv_data)
                col_num+=1

        except Exception as e:
            headings = driver.find_elements_by_tag_name("dt")
            details = driver.find_elements_by_tag_name("dd")
            tv_data = {}
            for i in range(len(headings)):
                tv_data[headings[i].get_attribute('textContent')] = details[i].get_attribute('textContent')
            all_data.append(tv_data)

    headings = set()
    for item in all_data:
        headings |= set(item.keys())

    clean_data = [headings]

    for tv in all_data:
        tv_data = []
        for item in clean_data[0]:
            tv_data.append(tv.get(item))
        clean_data.append(tv_data)


    with open("sony.csv", "w+", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(clean_data)


                # print("*********" + heading + "*********")
                # for det in details:
                #     print(det.get_attribute("textContent"))


    driver.close()
