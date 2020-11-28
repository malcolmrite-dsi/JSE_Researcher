# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 18:17:00 2020

@author: Malcolm Wright
"""

from selenium import webdriver

url = "https://www.sharedata.co.za/v2/Scripts/Glossies.aspx?c=ABG&x=JSE"

driver = webdriver.Chrome()

driver.get(url)