import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import mechanize

from myconfig import *

############
## Global ##
############

url_dict = {}

#############
## Helpers ##
#############


# Given a URL, retrieve it's page soup
def get_page(url):
    print("Fetching: ", url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response
    # soup = BeautifulSoup(response.text, "html.parser")
    # return soup


def html_response_to_soup(response):
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


# Sends email
def send_email(to_addr, subject, text):
    if not isinstance(to_addr, list):
        to_addr_list = [to_addr]
    else:
        to_addr_list = to_addr
    return requests.post(
        mailgun_url,
        auth=('api', mailgun_api_key),
        data={"from": mailgun_from,
              "to": to_addr_list, "subject": subject, "text": text}
    )


# Detects when registration is open
def is_registration_open(soup):
    # if there isn't "registration will open" on the page, email
    if str(soup).lower().find("registration has been closed") > -1:
        return False
    if str(soup).lower().find("registration will open") == -1:
        # make sure it's not giving a 404
        if str(soup).lower().find("404: page not found") > -1:
            print("404: page not found")
            return False
        return True
    return False


def is_registration_closed(soup):
    if str(soup).lower().find("registration has been closed") > -1:
        return True
    return False


# Fetches list of manually listed urls from Dropbox
def fetch_list_of_events_from_dropbox_url():
    response = get_page(dropbox_url)
    event_url_list = response.text.split('\n')
    # Filter out any events that start with "#", use that as comments
    event_url_list = [url for url in event_url_list if (
        url[0:1] != '#' and len(url) > 5)]
    print("Events found: ", len(event_url_list))
    url_list = [url for url in event_url_list if url not in url_dict]
    print("Net events found: ", len(url_list))
    return url_list


# Given a url with registration open, it'll attempt to fill out the form and submit
def fill_out_form(url):
    br = mechanize.Browser()
    br.open(url)
    br.select_form(id="registration-form")
    br['field_registration_name[und][0][value]'] = name
    br['anon_mail'] = email
    response = br.submit()
    return response


# Main infinite loop
def watcher():
    while True:
        print(f"Starting loop: {datetime.now()}")
        event_url_list = fetch_list_of_events_from_dropbox_url()
        for url in event_url_list:
            html_response = get_page(url)
            soup = html_response_to_soup(html_response)
            if (is_registration_open(soup)):
                print("Sending email...", datetime.now())
                email_response = send_email(
                    to_addr=[email_to_addr],
                    subject="Registration open!",
                    text=url
                )
                print("Email response: ", email_response)

                if (url not in url_dict):
                    print("Attempting to submit form", datetime.now())
                    response = fill_out_form(url)
                    print("Response of submitting: ", response)
                    url_dict[url] = True
                else:
                    print("Already submitted form")

            else:
                if is_registration_closed(soup):
                    print("Registration closed! Removing from list")
                    url_dict[url] = True
                    print("Added to url blacklist, skipping from now on")
                else:
                    print("Registration not open for", url)
        # next time run 1 second after a minute starts
        sleep_seconds = 60 - datetime.now().second
        print(
            f"Sleeping for {sleep_seconds} seconds. {datetime.now()}\n\n")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    print(f"STARTING...{datetime.now()}\n")
    watcher()
