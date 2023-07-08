from flask import Flask,request,render_template
import pytesseract as pytes
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
import cv2
from PIL import Image
import requests
import json
pytes.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
app=Flask(__name__,template_folder="template")
@app.route("/")
@app.route("/yorosis")
def home():
    return render_template("image_text.html")
@app.route("/predict",methods=["POST","GET"])
def image_text_conversion():
    if request.method=="POST":
        image_file = request.files['image']
        image_data = image_file.read()
        nparr = np.fromstring(image_data, np.uint8)
        ima2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        text = pytes.image_to_string(ima2, lang="eng+fra", config='--oem 3 --psm 6')

        #create the pattern to find the date
        ##tex="DATE: 12/09/1998 or 02-06-1996 or 02-jun-1998 or Aug 20,1993 or invoice date:02-06-1996 "
        date_pattern1 = re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}')
        date_pattern2 = re.compile(r'\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2,4}', re.IGNORECASE)
        date_pattern3 = re.compile(r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?) \d{1,2}, \d{4}',re.IGNORECASE)
        date_matches1 = date_pattern1.findall(text)
        date_matches2 = date_pattern2.findall(text)
        date_matches3 = date_pattern3.findall(text)

        # create the pattern to find the mail
        # email="Email: jone.do@gmail.com"
        email_pattern1 = r"(?i)email\s*:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        email_pattern2 = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        email_matches1 = re.search(email_pattern1, text)
        email_matches2 = re.search(email_pattern2, text)

        #create the pattern to find all country mobile number
        mobile_pattern1 = re.compile(r'\+91\s\d{10}|\+91\s\d{5}\s\d{5}')#india
        mobile_pattern2 = r"\d{10}" #india
        mobile_pattern3 = re.compile(r"\(\d{3}\) \d{3}-\d{4}|\d{3}-\d{3}-\d{4}")#us
        mobile_pattern4 = re.compile(r"\+1 \d{3}-\d{3}-\d{4}")#us
        mobile_pattern5 = re.compile(r"(^\+44\s\d{4}\s\d{6}$)|(^(0\d{4}|\(0\d{4}\))\s\d{6}$)")#uk
        mobile_pattern6 = re.compile(r"\+81 0\d{2}-\d{4}-\d{4}") #japan
        mobile_pattern7 = re.compile(r"\+49 01\d{1}-\d{7,8}")#germany
        mobile_pattern8 = re.compile(r"\+33 0[67]\d{8}")#france
        mobile_matches1 = re.findall(mobile_pattern1,text)
        mobile_matches2 = re.findall(mobile_pattern2, text)
        mobile_matches3 = re.findall(mobile_pattern3, text)
        mobile_matches4 = re.findall(mobile_pattern4, text)
        mobile_matches5 = re.findall(mobile_pattern5, text)
        mobile_matches6 = re.findall(mobile_pattern6, text)
        mobile_matches7 = re.findall(mobile_pattern7, text)
        mobile_matches8 = re.findall(mobile_pattern8, text)


        # create the pattern to find the address
        address_pattern = re.compile(r'\b(?:\d+,\s*)?[A-Za-z ]+\b')
        address_matches = address_pattern.findall(text)

        # create the pattern in invoice no
        invoice_pattern1 = r"(?i)invoice no\s*:\s*(\d+)"
        invoice_pattern2 = r"(?i)invoice no\s*#\s*(\d+)"
        invoice_pattern3 = r"(?i)invoice\s*#\s*(\d+)"
        invoice_pattern4 = r"(?i)^INVOICE NO # \d{6}$"
        invoice_matches1 = re.search(invoice_pattern1, text)
        invoice_matches2 = re.search(invoice_pattern2, text)
        invoice_matches3 = re.search(invoice_pattern3, text)
        invoice_matches4 = re.findall(invoice_pattern4,text)

        # create the pattern in sub_total
        subtotal_pattern1 = r'(?i)subtotal\s*\$[\d,]+\.\d+'
        subtotal_pattern2 = r'(?i)subtotal\s*[\d,]+\.\d+'
        subtotal_matches1 = re.findall(subtotal_pattern1, text)
        subtotal_matches2 = re.findall(subtotal_pattern2, text)

        # create the pattern in discount
        discount_pattern1 = r"Discount\s\((-?\d+\.\d+)\)"
        discount_pattern2 = r"(?i)discount\s*\d+\.\d+"
        discount_match1 = re.findall(discount_pattern1, text)
        discount_match2 = re.findall(discount_pattern2, text)

        # create the pattern in total
        total_pattern1 = r'(?i)balance due\s\$[\d,]+\.\d+'
        total_pattern2 = r'(?i)balance due\s*[\d,]+\.\d+'
        total_pattern3 = r'(?i)total\s\$[\d,]+\.\d+'
        total_pattern4 = r'(?i)total\s*[\d,]+\.\d+'
        total_matches1 = re.findall(total_pattern1, text)
        total_matches2 = re.findall(total_pattern2, text)
        total_matches3 = re.findall(total_pattern3, text)
        total_matches4 = re.findall(total_pattern4, text)

        # create the  pattern to find in url
        url_pattern=re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
        url_matches=re.findall(url_pattern,text)

        # create the pattern to find the website
        website_pattern=re.compile(r"(?:https?://)?(?:www\.)?[-\w]+\.[\w]{2,3}(?:\.[\w]{2})?")
        website_matches=re.findall(website_pattern,text)
        # create the countors to find the table data inside table.
        gray = cv2.cvtColor(ima2, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_contour_area = 1000
        table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]
        table_boundaries = [cv2.boundingRect(cnt) for cnt in table_contours]
        tables = []
        for x, y, w, h in table_boundaries:
            table_image = gray[y:y + h, x:x + w]
            text = pytes.image_to_string(table_image)
            rows = text.strip().split('\n')
            table_data = [row.split() for row in rows]
            table = {
                'table_data': table_data,
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
            tables.append(table)

        data={}
        if date_matches1:
            data["Date"]=date_matches1
        elif date_matches2:
            data["Date"] = date_matches2
        elif date_matches3:
            data["Date"] = date_matches3
        else:
            print("This type date format not found")
        if email_matches1:
            data["Email"] = email_matches1.group(1)
        elif email_matches2:
            data["Email"] = email_matches2.group(1)
        else:
            print("email format not found")

        if mobile_matches1:
            data["Mobile No"]=mobile_matches1
        elif mobile_matches2:
            data["Mobile No"] = mobile_matches2
        elif mobile_matches3:
            data["Mobile No"] = mobile_matches3
        elif mobile_matches4:
            data["Mobile No"] = mobile_matches4
        elif mobile_matches5:
            data["Mobile No"] = mobile_matches5
        elif mobile_matches6:
            data["Mobile No"] = mobile_matches6
        elif mobile_matches7:
            data["Mobile No"] = mobile_matches7
        elif mobile_matches8:
            data["Mobile No"] = mobile_matches8
        else:
            print("this type mobile number not found")

        #if address_matches:
            #data["Address"]=address_matches
        #else:
            #print("this type address not found")
        if invoice_matches1:
            data["INVOICE NO"] = invoice_matches1.group(1)
        elif invoice_matches2:
            data["INVOICE NO"] = invoice_matches2.group(1)
        elif invoice_matches3:
            data["INVOICE NO"] = invoice_matches3.group(1)
        elif invoice_matches4:
            data["INVOICE NO"]=invoice_matches4
        if subtotal_matches1:
            data["SUBTOTAL"] = subtotal_matches1
        elif subtotal_matches2:
            data["SUBTOTAL"] = subtotal_matches2
        else:
            print("this type subtotal not found")
        if discount_match1:
            data["discount"] = discount_match1
        elif discount_match2:
            data["discount"] = discount_match2
        else:
            print("this type of discount format not found")
        if total_matches1:
            data["TOTAL"] = total_matches1
        elif total_matches2:
            data["TOTAL"] = total_matches2
        elif total_matches3:
            data["TOTAL"] = total_matches3
        elif total_matches4:
            data["TOTAL"] = total_matches4
        if url_matches:
            data["URL"]=url_matches
        else:
            print("url not match")
        #if website_matches:
            #data["Website"]=website_matches
        #else:
            #print("the website not match")

        #data["Table"]=table
        json_data = json.dumps(data, indent=4)
        # print(json_data)
        return render_template("image_text.html", **locals())
if __name__ == "__main__":
            app.run(debug=True, host='0.0.0.0', port=5000)


