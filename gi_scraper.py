from selenium import webdriver
from six.moves import urllib
from gevent import monkey
import gevent
from PIL import Image
import tqdm
import time
import json
import sys
import os

# Config
download_img_path = "img/"
req_header = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"

# Images
search_words = ['hotdog', 'not hotdog']
num_images = [1000, 300]
start_idx = [0, 0]

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()


def write_img_file(pbar, img_item):
    req = urllib.request.Request(img_item[1])
    req.add_header('User-Agent', req_header)
    try:
        # img_data = urllib.request.urlopen(req).read()
        img_data = urllib.request.urlopen(req)
    except:
        pbar.update()
        return

    # Problem encountered : data downloaded not adequate
    # image with RIFF format, url returns html page <not available in your country>
    # not_adequate = ["RIFF", "html"]
    # if any(s in str(img_data) for s in not_adequate):
    #   return

    try:
        img = Image.open(img_data)
    except:
        pbar.update()
        return

    # Some image have alpha channel -> get rid of it to be save as JPEG
    img = img.convert('RGB')
    img.save(img_item[0])
    pbar.update()
    return


def get_images(driver, folder_path, num):
    count = 0
    images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    extensions = {"jpg", "jpeg", "png"}
    img_list = []

    for img in images:
        if count >= num:
            break

        img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
        img_type = json.loads(img.get_attribute('innerHTML'))["ity"]

        if img_type not in extensions:
            continue

        file_name = folder_path + "/" + str(count) + "." + img_type
        img_list.append((file_name, img_url))
        count += 1

    pbar = tqdm.tqdm(total=len(img_list))
    tasks = [gevent.spawn(write_img_file, pbar, img_item)
             for img_item in img_list]
    gevent.joinall(tasks)
    print("DONE\n")


def scroll(driver, num_scrolls):

    for _ in range(num_scrolls):
        for __ in range(10):
            # scrolls to show all 400 images
            driver.execute_script("window.scrollBy(0, 1000000)")
            time.sleep(0.2)
        # click "show more results"
        time.sleep(0.5)
        try:
            driver.find_element_by_xpath(
                "//input[@value='Plus de résultats']") .click()
            time.sleep(0.5)
        except Exception as e:
            print("    show more results failed -> exception: " + str(e))


def search(search_txt, num, idx):

    if not os.path.exists(download_img_path):
        os.makedirs(download_img_path)

    folder_path = download_img_path + search_txt.replace(" ", "_")

    # Create folders for each search
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    url = "https://www.google.co.in/search?q=" + \
        search_txt + "&source=lnms&tbm=isch"
    driver = webdriver.Chrome(
        executable_path=r"/usr/lib/chromium/chromedriver")
    driver.get(url)

    # Google images -> 400 images before "show more results"
    # start scrolling to load enough images
    num_scrolls = int((num + idx) / 400 + 1)
    scroll(driver, num_scrolls)
    get_images(driver, folder_path, num)


for i in range(len(search_words)):
    w = search_words[i]
    print('search for ' + str(num_images[i]) + ' images of ' + w)
    search(w, num_images[i], start_idx[i])

print('DONE')
