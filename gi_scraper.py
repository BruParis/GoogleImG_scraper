from selenium import webdriver
from six.moves import urllib
import time
import json
import sys
import os

# Config
download_img_path = "img/"
req_header = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22"

# Images
search_words = ['hotdog', 'not hotdog']
num_images = [20, 30]
start_idx = [0, 0]

def write_img_file(file_name, img_url, img_type):
  req = urllib.request.Request(img_url)
  req.add_header('User-Agent', req_header)
  raw_img = urllib.request.urlopen(req).read()
  f = open(file_name, "wb")
  f.write(raw_img)
  f.close()

def get_images(driver, folder_path, num):
    count = 0
    images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    extensions = {"jpg", "jpeg", "png", "gif"}

    for img in images:

        if count > num:
          break
        
        img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
        img_type = json.loads(img.get_attribute('innerHTML'))["ity"]

        if img_type not in extensions:
          continue

        # open each google image to access full size
        file_name = folder_path + "/" + str(count) + "." + img_type
        write_img_file(file_name, img_url, img_type)
        ratio = 100 * count / num
        sys.stdout.write("progress: " + str(int(ratio)) + "%\r")
        sys.stdout.flush()
        sys.stdout.write("\r")
        time.sleep(0.1)
        
        count += 1
    
    print("\n")

def scroll(driver, num_scrolls):

    for _ in range(num_scrolls):
        for __ in range(10):
            # scrolls to show all 400 images
            driver.execute_script("window.scrollBy(0, 1000000)")
            time.sleep(0.2)
        # click "show more results"
        time.sleep(2.5)
        try:
            driver.find_element_by_xpath("//input[@value='Plus de résultats']") .click()
            time.sleep(2.5)
        except Exception as e:
            print("    show more results failed -> exception: " + str(e))

def search(search_txt, num, idx):

    if not os.path.exists(download_img_path):
      os.makedirs(download_img_path)

    folder_path = download_img_path + search_txt.replace(" ", "_")

    # Create folders for each search
    if not os.path.exists(folder_path):
      os.makedirs(folder_path)

    url = "https://www.google.co.in/search?q=" + search_txt + "&source=lnms&tbm=isch"
    driver = webdriver.Chrome(executable_path=r"/usr/lib/chromium/chromedriver")
    driver.get(url)

    # Google images -> 400 images before "show more results"
    # start scrolling to load enough images
    num_scrolls = int((num + idx)/ 400 + 1)
    scroll(driver, num_scrolls)
    get_images(driver, folder_path, num)

for i in range(len(search_words)):
    w = search_words[i]
    print('search for ' + str(num_images[i]) + ' images of ' + w)
    search(w, num_images[i], start_idx[i])

print('DONE')
