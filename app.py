import csv
from sre_constants import SUCCESS
import time
from pprint import pprint
import requests
from csv import DictReader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image
import re
import os

def get_first_img(string):
    place = string.find(',')
    output = string[0:place]
    if output[len(output) - 1] != 'g':
        output += 'g'
    return output

def convert_specs(title, data):
    if data == ' ' or data == '':
        data = '-'
    output = {
        'title': title,
        'data': data
    }
    return output

def fix_description(description):
    soup = BeautifulSoup(description, 'lxml')
    output = soup.get_text()
    output = re.sub("\n", "", output)
    if len(output) > 418:
        output = output[0:418]
    return output.strip('\n')

def get_product_data(product):
    spec_list = []
    spec_list.append(convert_specs('MATERIAL', product['Meta: materialtubing']))
    spec_list.append(convert_specs('HEIGHT', product['Meta: height']))
    spec_list.append(convert_specs('WIDTH', product['Meta: width']))
    spec_list.append(convert_specs('DEPTH', product['Meta: depth']))
    spec_list.append(convert_specs('WEIGHT', product['Meta: weight']))
    spec_list.append(convert_specs('FOOT PRINT', product['Meta: foot-print']))
    spec_list.append(convert_specs('MADE IN USA', product['Meta: made-in-usa'].upper()))
    output = {
        'id' : product["\ufeffID"],
        'name' : product['Name'],
        'sku' : product['SKU'],
        'description' : fix_description(product['Short description']),
        'main image' : get_first_img(product['Images']),
        'featured images 1' : product['Meta: features-1-image'],
        'featured title 1' : product['Meta: features-1-'],
        'featured images 2' : product['Meta: features-2-images'],
        'featured title 2' : product['Meta: features-2'],
        'featured images 3' : product['Meta: features-3-image'],
        'featured title 3' : product['Meta: features-3'],
        'spec list' : spec_list
    }
    return output

def convert_title(title):
    output = ''
    for letter in title:
        if letter == ' ' or letter == '/':
            output += '-'
        else:
            output += letter

    return output.lower()

def login(driver):
    driver.get('https://straydogstrength.com/wp-admin/')
    username = 'Straydog Strength'
    password = '2021weon1!'
    driver.find_element(By.CSS_SELECTOR, "#jetpack-sso-wrap > a.jetpack-sso-toggle.wpcom").click()
    user_button = driver.find_element(By.ID, "user_login")
    driver.implicitly_wait(10)
    user_button.click()
    user_button.send_keys(username)
    pass_button = driver.find_element(By.ID, "user_pass")
    driver.implicitly_wait(10)
    pass_button.click()
    pass_button.send_keys(password)
    driver.find_element(By.ID, "wp-submit").click()

def upload_pdf(id, file_name, product_title, driver):
    print('uploading file...')
    file_path = "/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/" + file_name
    driver.get('https://straydogstrength.com/wp-admin/media-new.php')
    try:    
        driver.find_element(By.XPATH, "//*[@id=\"async-upload\"]").send_keys(file_path)
        driver.find_element(By.ID, "html-upload").click()
    except:
        print('try again - product name: ' + product_title)
        driver.get('https://straydogstrength.com/wp-admin/media-new.php')
        driver.implicitly_wait(3)
        driver.find_element(By.XPATH, "//*[@id=\"async-upload\"]").send_keys(file_path)
        driver.find_element(By.ID, "html-upload").click()
    #--add to product page
    pdf_file_url = 'https://straydogstrength.com/wp-content/uploads/2022/06/' + file_name
    post_url = 'https://straydogstrength.com/wp-admin/post.php?post='+ id + '&action=edit'
    driver.get(post_url)
    driver.find_element(By.XPATH, "//*[@id=\"jet-engine-cpt-1\"]/div[2]/div/div/div/div[1]/button[6]").click()
    driver.find_element(By.ID, "pdf-link").clear()
    driver.find_element(By.ID, "pdf-link").send_keys(pdf_file_url)
    # --paste title
    driver.find_element(By.XPATH, "//*[@id=\"title\"]").clear()
    driver.find_element(By.XPATH, "//*[@id=\"title\"]").send_keys(product_title)
    # --click update
    driver.find_element(By.CSS_SELECTOR, "#publish").click()
    # --delete pdf file
    # If file exists, delete it ##
    if os.path.isfile(file_name):
        os.remove(file_name)
        print('deleted file')
    else:    ## Show an error ##
        print("Error: %s file not found" % file_name)

def create_pdf(product):
    # create pdf
    print('creating pdf - Product name: ' + product['name'])
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=0, margin = 0.0)

    # add fonts
    pdf.add_font('Teko Regular', '', f"/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/pyfpdf/spec-sheet/Teko-Regular.ttf")
    pdf.add_font('Teko Bold', '', f"/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/pyfpdf/spec-sheet/Teko-Bold.ttf")
    pdf.add_font('Teko Light', '', f"/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/pyfpdf/spec-sheet/Teko-Light.ttf")
    pdf.add_font('Teko SemiBold', '', f"/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/pyfpdf/spec-sheet/Teko-SemiBold.ttf")
    pdf.add_font('Teko Medium', '', f"/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/pyfpdf/spec-sheet/Teko-Medium.ttf")

    # red rectangle
    pdf.set_fill_color(r=204, g=32, b=38)
    pdf.rect(0, 0, 255.0, 20.0, style='F')

    # SD LOGO
    img = "/Users/danielpurdy/Desktop/Dan's-Digital/Clients/Straydog Strength/straydog 2.0/dev-prodjects/pdf Generator/SD header logo.png"
    pdf.image(img, 2.5, 2.5, link='', type='', w=70, h=15)

    # sku and year
    year = '2022'
    sku_year = 'SKU: ' + product['sku'] + ' | YEAR: ' + year
    pdf.set_font('Teko Light', '', 18)
    pdf.set_text_color(r=255, g=255, b=255)
    pdf.set_xy(160, 0)
    pdf.cell(h=20, align='C', w=50, txt=sku_year, border=0)

    # product title
    product_title = product['name']

    product_title_height = 50
    y_product_title = 25
    if len(product_title) > 14 and len(product_title) <= 25:
        product_title_height = 15
        y_product_title = 33
    elif len(product_title) > 25:
        product_title_height = 15
    else:
        y_product_title = 28

    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font('Teko Medium', '', 40)
    # pdf.set_fill_color(r=215, g=215, b=215)
    pdf.set_xy(5, y_product_title)
    pdf.multi_cell(h=product_title_height, w=85, txt=product_title, border=0, align='L', fill=0)

    # Main image
    img = Image.open(requests.get(product['main image'], stream=True).raw)
    pdf.image(img, 90, 25, link='', type='', w=115, h=115)

    # --spec table---
    # -spec title
    y_spec_table = 85
    pdf.set_font('Teko Medium', '', 30)
    pdf.set_xy(5, y_spec_table)
    pdf.cell(align='L', w=70, txt='SPECS', border=0)

    # -red line under title
    pdf.set_line_width(0.5)
    pdf.set_draw_color(r=204, g=32, b=38)
    pdf.line(5, y_spec_table + 12, 85, y_spec_table + 12)

    # -spec text
    # x_title = 5
    y_title = y_spec_table + 15
    # x_data = 40
    y_data = y_spec_table + 15.5
    # x_line = 5
    y_line = y_spec_table + 24
    for spec in product['spec list']:
        pdf.set_font('Teko Regular', '', 20)
        pdf.set_xy(5, y_title)
        pdf.cell(align='L', w=45, txt=spec['title'], border=0, fill=0)
        pdf.set_font('Teko Regular', '', 18)
        pdf.set_xy(40, y_data)
        pdf.cell(align='R', w=45, txt=spec['data'], border=0, fill=0)
        pdf.line(5, y_line, 85, y_line)

        y_title += 12
        y_data += 12
        y_line += 12

    # product description
    description = product['description']
    pdf.set_font('Teko Regular', '', 20)
    pdf.set_fill_color(r=215, g=215, b=215)
    pdf.set_xy(90, 145)
    pdf.multi_cell(w=115, txt=description, border=0, align='L')

    # ---features
    # features data
    features_url1 = product['featured images 1']
    features_url2 = product['featured images 2']
    features_url3 = product['featured images 3']
    feature_title1 = product['featured title 1']
    feature_title2 = product['featured title 2']
    feature_title3 = product['featured title 3']

    # --features main title
    featured_width = 63
    y_featured_image = 205
    pdf.set_font('Teko Medium', '', 30)
    pdf.set_xy(5, y_featured_image - 15)
    pdf.cell(align='L', w=70, txt='FEATURES', border=0)

    pdf.set_font('Teko Regular', '', 20)
    y_featured_title = y_featured_image + 65
    # --featured images
    if features_url1 != '':
        # - image 1
        img = Image.open(requests.get(features_url1, stream=True).raw)
        pdf.image(img, 5, y_featured_image, link=features_url1, type='', w=featured_width, h=featured_width)
        # -title 1
        pdf.set_xy(5, y_featured_title)
        pdf.multi_cell(w=featured_width, txt=feature_title1, border=0, align='C', fill=0)

    if features_url2 != '':
        # - image 2
        img = Image.open(requests.get(features_url2, stream=True).raw)
        pdf.image(img, 74, y_featured_image, link=features_url2, type='', w=featured_width, h=featured_width)
        # # -title 2
        pdf.set_xy(74, y_featured_title)
        pdf.multi_cell(w=featured_width, txt=feature_title2, border=0, align='C', fill=0)

    bool; img_exists = features_url3.isnumeric()
    if features_url3 != '' and img_exists == False:
        # - image 3
        img = Image.open(requests.get(features_url3, stream=True).raw)
        pdf.image(img, 143, y_featured_image, link=features_url3, type='', w=featured_width, h=featured_width)
        # # -title 3
        pdf.set_xy(143, y_featured_title)
        pdf.multi_cell(w=featured_width, txt=feature_title3, border=0, align='C', fill=0)

    # ---footer
    # --domain name
    pdf.set_fill_color(r=215, g=215, b=215)
    pdf.set_font('Teko Light', '', 18)
    pdf.set_xy(0, -10)
    pdf.cell(align='C', w=210, h=10, txt='STRAYDOGSTRENGTH.COM', border=0, fill=1)
    
    file_name = convert_title(product['name']) + ".pdf"
    # output pdf
    try:
        pdf.output(file_name)
        print('PDF SUCCESS - Product name: ' + product['name'])
    except:
        print('PDF FAIL - Product name: ' + product['name'])

    return file_name

# ======== MAIN FUNC =========
if __name__ == "__main__":
    start_time = time.time()
    # get data from csv file to list of dics
    with open("product_data.csv", "r") as f:
        csv_reader = csv.DictReader(f)
        product_records = list(csv_reader)

    # get needed data
    pdf_data = []
    for product in product_records:
        if product['Parent'] == '':
            pdf_data.append(get_product_data(product))

    # get featured image 3
    HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

    base_media_url = 'https://straydogstrength.com/?attachment_id='
    # print('\ngetting featured images 3...')
    
    # for product in pdf_data:
    #     if product['featured images 3'] != '' and product['featured images 3'].isnumeric():
    #         page = requests.get(base_media_url + product['featured images 3'], headers=HEADERS)
    #         soup = BeautifulSoup(page.content, 'html.parser')
    #         path = "#post-" + product['featured images 3'] + " > div > div > p > a"
    #         for link in soup.select(path):
    #             product['featured images 3'] = link.get('href')
    # print('done - Time: ' + str(time.time() - start_time))

    # creating webdriver
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()

    # login to wordpress
    login(driver)

    # create and upload and delete pdf docs
    product_total = len(pdf_data)

    for count, product in enumerate(pdf_data):
        if product['featured images 3'] != '' and product['featured images 3'].isnumeric():
            page = requests.get(base_media_url + product['featured images 3'], headers=HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')
            path = "#post-" + product['featured images 3'] + " > div > div > p > a"
            for link in soup.select(path):
                product['featured images 3'] = link.get('href')

        file_name = create_pdf(product)
        upload_pdf(product['id'], file_name, product['name'], driver)
        
        print('product count: ' + str(count) + ' - total: ' + str(product_total) + '\n')
    
    driver.quit()
    minutes = (time.time() - start_time) / 60 
    print('Run Time - Minutes: ' + str(minutes))