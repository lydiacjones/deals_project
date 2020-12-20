# Web Scraper Project
# Lydia Jones

import urllib.request
from bs4 import BeautifulSoup
import re
import os
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_deals():
    #Get deals with urllibrequest
    url = "https://dealsea.com/Laptops-Desktops-Tablets/b?node=3001"
    main_url = 'https://dealsea.com/'
    response = urllib.request.urlopen(url)

    data = response.read().decode()
    soup = BeautifulSoup(data, 'html.parser')
   
    table = []
    my_deals = open('my_deals.txt', 'w')    #open file
    # loop to sort into list with embedded dictionary
    for d in soup.findAll('div', class_='dealbox'):    
        # Get deal name    
        find_a = d.findAll('a')    
        deal_name = str(find_a[1].find(text=True).encode('utf-8'))  

        # Get vendor name    
        find_a = d.findAll('a')    
        vendor_name = str(find_a[2].find(text=True))

        # Get Vendors    
        vendors = d.find_all(href=re.compile(r"\/j\/4\/\?pid\="))    
        vendors_dict = {}    
        for v in vendors:        
            vendor_name = str(v.find(text=True).encode('utf-8'))        
            vendor_link = main_url + str(v['href'])        
            if vendor_name not in vendors_dict:            
                vendors_dict[vendor_name] = []        
            vendors_dict[vendor_name].append(vendor_link) 

        # Get deal content    
        deal_content = d.findAll('div', class_='dealcontent')[0].find(text=True)
        # Add information to the table    
        table.append([deal_name, vendors_dict, deal_content])

        #Format the scraped details to look better
        deal_name = deal_name.strip("b'")
        deal_name = 'Deal + Price: ' + deal_name + '\n'
        vendors_dict = str(vendors_dict).strip('"b{}"')
        vendors_dict =  'Vendor + URL: ' + vendors_dict + '\n' + '___________________________________________________' + "\n"
        deal_content = deal_content.strip()
        print(deal_name)
        print(vendors_dict)
        print(deal_content)

        #open and write to .txt; close .txt
        my_deals = open('my_deals.txt', 'a')    #open
        my_deals.write(str(deal_name))     #write
        my_deals.write(vendors_dict)    #write
        # my_deals.write(str(deal_content))    #write
        my_deals.close()      #close
    
#Twilio - send text message
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')   # Enter your auth token from twilio
    client = Client(account_sid, auth_token)
    message = client.messages \
                    .create(
                        body=deal_name + vendors_dict,
                        from_=os.getenv('TWILIO_FROM_NUMBER'),
                        to=os.getenv('TO_PHONE_NUMBER')
                    )

#Sending Emails
    # me == my email address
    # you == recipient's email address
    me = os.getenv('FROM_EMAIL_ADDRESS')
    you = os.getenv('TO_EMAIL_ADDRESS')

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Dealsea.com Deals"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org" #ignore
    html_deals = soup.findAll('div', class_='dealbox')
    html = "<html> {} </html>".format(''.join(str(j) for j in html_deals))

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()

    mail.starttls()

    mail.login(os.getenv('FROM_EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD')) #Enter your own email and password

    mail.sendmail(me, you, msg.as_string()) #from and to address

    mail.close()

get_deals()


