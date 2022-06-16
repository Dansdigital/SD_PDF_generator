import csv
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

start_time = time.time()
# ========================
# get csv file into a list of python dic's
# ========================
with open("product_data.csv", "r") as f:
    csv_reader = csv.DictReader(f)
    product_records = list(csv_reader)

def get_check_data(product):
    output = {
        'name': product['Name'],
        'sku': product['SKU'],
        'DONE' : ''
    }
    return output

list; check_data = []
for product in product_records:
    if product['Parent'] == '':
        check_data.append(get_check_data(product))

for product in check_data:
    pprint(product)
    print('===========')

with open('check_data.csv', 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=check_data[0].keys())
    wr.writeheader()
    wr.writerows(check_data)


print('Run Time: ' + str(time.time() - start_time))