from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException
import csv
import time
import json

def wait_for_load(driver, delay, frequency, element):
    retries = 0
    while(retries<5):
        try:
            myElem = WebDriverWait(driver, delay, poll_frequency = frequency).until(EC.presence_of_element_located((By.ID, element)))
            print("Page is ready!")
            return
        except TimeoutException:
            print("Loading took too much time!")
            retries+=1

def get_clicker_links(driver, card_link, links):
    prev_link = card_link + "//button[@aria-label='Previous']"
    next_link = card_link + "//button[@aria-label='Next']"
    link_path = card_link + "//div/div/div/a"
    price_path = card_link + "//span[@class='cm-shop-card__price-num']"
    model_path = card_link + "//span[@class='cm-shop-card__serial']"
    prev_is_disabled = False

    while not prev_is_disabled:
        driver.find_element_by_xpath(prev_link).click()
        try:
            driver.find_element_by_xpath(prev_link + "[@aria-disabled='true']")
            prev_is_disabled = True
        except Exception as e:
            pass

    button_num = 0
    flag = 1
    while(flag):
        try:
            #check if next button is disabled
            driver.find_element_by_xpath(next_link + "[@aria-disabled='true']")
            flag = 0
        except Exception as e:
            pass

        button_num+=1
        button_link = card_link + "//div[@class='slick-track']/div["+ str(button_num) + "]"
        try:
            driver.find_element_by_xpath(button_link).click()
        except Exception as e:
            pass

        link = driver.find_element_by_xpath(link_path).get_attribute("href")
        model = driver.find_element_by_xpath(model_path).get_attribute("textContent")
        try:
            price = driver.find_element_by_xpath(price_path).get_attribute("textContent")
        except NoSuchElementException:
            price = None

        if not any(substr in link for substr in ("tv-care-pack", "tv-carepack")):
            links[link] = [price, model]

        driver.find_element_by_xpath(next_link).click()

    #get last model link
    button_num+=1
    button_link = card_link + "//div[@class='slick-track']/div["+ str(button_num) + "]"
    try:
        driver.find_element_by_xpath(button_link).click()
    except Exception as e:
        pass

    link = driver.find_element_by_xpath(link_path).get_attribute("href")
    model = driver.find_element_by_xpath(model_path).get_attribute("textContent")
    try:
        price = driver.find_element_by_xpath(price_path).get_attribute("textContent")
    except NoSuchElementException:
        price = None

    if not any(substr in link for substr in ("tv-care-pack", "tv-carepack")):
        links[link] = [price, model]

    return links


if(__name__=="__main__"):
    init = time.time()
    driver = webdriver.Firefox() #geckodriver
    delay = 5 #seconds
    frequency = 3 #check for element 3 times/delay

    driver.get("https://www.samsung.com/in/tvs/all-tvs/")
    wait_for_load(driver, delay, frequency, 'content')
    element = driver.find_element_by_class_name("cm-cookie-geo__close-cta.js-geo-close").click()

    while(1):
        # scroll down till end of page
        WebDriverWait(driver, delay, poll_frequency = frequency).until(EC.invisibility_of_element_located((By.CLASS_NAME,
              "cm-loader.cm-loader-type2")))
        try:
            driver.find_element_by_class_name("s-btn-text.type2.s-ico-down").click()

        except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) :
            break;

    links = {} #maps dict[tv_link] = [tv_price, model_num]
    card_num = 0
    while(1):
        card_link = "//div[@class='shop-grid']//div[@class='shop-grid-col shop-col3' and @family-index=" + str(card_num) + "]"
        button_num = 0
        flag = 1

        try:
            driver.find_element_by_xpath(card_link)
        except Exception as e:
            break;

        clickers_exist = False

        while(flag):
            button_num+=1
            try:
                driver.find_element_by_xpath(card_link + "//button[@class='slick-prev slick-arrow']")
                clickers_exist = True
            except Exception as e:
                pass

            if clickers_exist:
                links = get_clicker_links(driver, card_link, links)
                break;

            else:
                try:
                    button_link = card_link + "//div[@class='slick-track']/div["+ str(button_num) + "]"
                    driver.find_element_by_xpath(button_link).click()
                except (NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException) as e:
                    break;

                link_path  = card_link + "//div/div/div/a"
                price_path = card_link + "//span[@class='cm-shop-card__price-num']"
                model_path = card_link + "//span[@class='cm-shop-card__serial']"
                link = driver.find_element_by_xpath(link_path).get_attribute("href")
                model = driver.find_element_by_xpath(model_path).get_attribute("textContent")
                try:
                    price = driver.find_element_by_xpath(price_path).get_attribute("textContent")
                except NoSuchElementException:
                    price = None


                if not any(substr in link for substr in ("tv-care-pack", "tv-carepack")):
                    links[link] = [price, model]
        card_num+=1

    # for link in links:
    #     print(link)

    all_data = []

    for link in links.keys():
        print(link)
        driver.get(link)
        wait_for_load(driver, delay, frequency, "specs")
        driver.find_element_by_class_name('s-btn-text.show_btn.s-ico-down').click()
        detail_section = driver.find_element_by_class_name("product-specs__highlights-list").find_elements_by_tag_name('li')

        tv_data = {}

        detail_sections = driver.find_elements_by_xpath("//ul[@class='product-specs__highlights-list']/li")
        for section in detail_sections:
            # print(section.get_attribute('innerHTML'))
            try:
                subsection = section.find_element_by_class_name('product-specs__highlights-desc-list')
                subheadings = subsection.find_elements_by_class_name('product-specs__highlights-sub-title')
                details = subsection.find_elements_by_class_name('product-specs__highlights-desc')

                for i in range(len(subheadings)):
                    tv_data[subheadings[i].get_attribute('textContent')] = details[i].get_attribute('textContent')
                    print(subheadings[i].get_attribute('textContent'), details[i].get_attribute('textContent'))

            except Exception as e:
                try:
                    details = section.find_element_by_class_name('product-specs__highlights-desc')
                    head = section.find_element_by_class_name('product-specs__highlights-title')
                    tv_data[head.get_attribute('textContent')] = details.get_attribute('textContent')
                    print(head.get_attribute('textContent'), details.get_attribute('textContent'))
                except Exception as e:
                    print(e)
                    print(section.get_attribute('innerHTML'))
                    pass

        tv_data["Price"] = links.get(link)[0]
        tv_data["Model"] = links.get(link)[1]
        tv_data["Link"] = link
        tv_data["Source"] = "website"
        tv_data["Brand"] = "Samsung"
        try:
            dimensions = tv_data["Set Size without Stand (WxHxD)"].split()
            tv_data['width'] = dimensions[0]
            tv_data['height'] = dimensions[2]
            tv_data['depth'] = dimensions[4]
            tv_data['height with stand'] = tv_data["Set Size with Stand (WxHxD)"].split()[2]
        except Exception as e:
            try:
                dimensions = tv_data["Set Size without Stand (WxHxD)"].split("*")
                tv_data['width'] = dimensions[0]
                tv_data['height'] = dimensions[1]
                tv_data['depth'] = dimensions[2]
                tv_data['height with stand'] = tv_data["Set Size with Stand (WxHxD)"].split("*")[1]
            except Exception as e:
                pass

        curvature = tv_data.get("Screen Curvature")

        if(curvature):
            tv_data["curved"] = "Curved"
        else:
            tv_data["curved"] = "Flat"
        wall_mount = tv_data.get("No Gap Wall-mount (Included)")
        if not wall_mount:
            tv_data["No Gap Wall-mount (Included)"] = "No"

        power = tv_data["Power Supply"].split()
        if(len(power)>1):
            tv_data["ac power"] = power[0]
            tv_data["frequency"] = power[1]


        all_data.append(tv_data)

    driver.close()
    print(time.time() - init)


    #process and clean data

    headings = set()
    for item in all_data:
        headings |= set(item.keys())

    clean_data = [headings]

    for tv in all_data:
        tv_data = []
        for item in clean_data[0]:
            tv_data.append(tv.get(item))
        clean_data.append(tv_data)


    with open("output.csv", "w+", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(clean_data)

    with open("config.json") as f:
        config = json.load(f)

    with open("master.csv", "a+", newline="") as f:
        reader = csv.reader(f)
        writer = csv.writer(f)
        headers = next(reader, None)
        for tv in clean_data:
            ls = []
            for head in headers:
                ls.append(clean_data.get(config.get(head)))
            writer.writerow(ls)
