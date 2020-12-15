#!/usr/bin/python3
from requests import Session
from lxml import html
from os import mkdir, makedirs, path
from urllib import parse
from getpass import getpass
from re import sub, search
from sys import exit

import argparse

from utilities import (session_get, session_post, clean_file_name,
        download_file, dump)
from Module import Module
from ModuleItem import ModuleItem


COURSE_URL = ''
CANVAS_URL = ''
COURSE_ID = ''
CANVAS_LOGIN_URL = ''
DOWNLOAD_PATH = 'modules/'


def login(username, password, session):
    resp = session_get(CANVAS_LOGIN_URL, session)
    postURL = resp.url
    
    payload = {
        'UserName': username,
        'Password': password,
        'AuthMethod': 'FormsAuthentication'
    }

    resp = session_post(postURL, session, payload)
    content = resp.content.decode('utf-8')
    tree = html.fromstring(resp.content)

    errorText = tree.xpath("//span[@id='errorText']/text()")

    if len(errorText) != 0:
        exit('Error: ' + errorText[0])

    samlResponse = tree.xpath('/html/body/form/input/@value')[0]

    payload = {
        'SAMLResponse': samlResponse
    }

    session_post(CANVAS_LOGIN_URL, session, payload)

    


def get_items(moduleNode):
    items = [ ]

    for itemNode in moduleNode.xpath(".//li[contains(@class, 'context_module_item')]"):
        item = ModuleItem()
        item.name = itemNode.xpath(".//span[@class='item_name']/span[@title]/@title")[0]
        item.itemType = itemNode.xpath(".//div/span[@class='type_icon']/@title")[0]
        item.modId = itemNode.attrib['id'].replace('context_module_item_', '')

        # Replace Page with WikiPage for consistency
        if item.itemType == "Page":
            item.itemType = "WikiPage"

        for cls in itemNode.classes:
            if cls.find(item.itemType) > -1:
                item.itemId = int(cls.replace(item.itemType + "_", ''))

        items.append(item)
        
    return items



def download_item(module, item, session):
    filename = clean_file_name(item.name)        
    moduleFilename = clean_file_name(module.name)

    fullPath = "{0}{1}/{2}".format(DOWNLOAD_DIR, moduleFilename, filename)

    print("  - Downloading ({0}-{1}) {2}...".format(item.itemType, item.itemId, item.name))

    if item.itemType == 'Attachment':
        download_file("{0}/courses/{1}/files/{2}/download".format(
            CANVAS_URL, COURSE_ID, item.itemId), session, fullPath)
    else:
        # Add .html extension for webpage downloads
        fullPath += ".html"
        download_file("{0}/courses/{1}/modules/items/{2}".format(CANVAS_URL, COURSE_ID, item.modId), session, fullPath)



def get_modules(session):
    print("Getting modules...\n")

    modules = [ ]

    resp = session_get('{0}/courses/{1}/modules'.format(CANVAS_URL, COURSE_ID), session)
    tree = html.fromstring(resp.content)
    moduleNodes = tree.xpath("//div[contains(@class, 'context_module') and contains(@class, 'item-group-condensed')]")

    # Last element is a blank module
    moduleNodes.pop()

    for moduleNode in moduleNodes:
        module = Module()
        module.name = moduleNode.attrib['aria-label']

        print("Found Module ", module.name)

        module.items = get_items(moduleNode)
        modules.append(module)

    print("")

    return modules



def download_modules(modules, session):
    if not path.exists(DOWNLOAD_DIR):
        makedirs(DOWNLOAD_DIR)

    for mod in modules:
        print("\nDownloading Module {0}...".format(mod.name))

        modDirName = clean_file_name(mod.name)
        modPath = DOWNLOAD_DIR + modDirName

        if not path.exists(modPath):
            makedirs(modPath)

        for item in mod.items:
            download_item(mod, item, session)



def main():
    global CANVAS_URL, COURSE_ID, CANVAS_LOGIN_URL, COURSE_URL, DOWNLOAD_DIR

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help=("Username in "
        "the form <school>/<username> or school email i.e. "
        "<username>@<school>.edu. For example, floridapoly/jdoe2512 or "
        "jdoe2512@floridapoly.edu)"))
    parser.add_argument('-c', '--course-url', required=True, help=("Url to "
        "Canvas course e.g. https://floridapolytechnic.instructure.com/"
        "courses/2242. Make sure you include https:// in the url."
        ))
    parser.add_argument('-d', '--download-dir', help="Path to download folder",
            default="modules/")

    args = parser.parse_args()

    username = args.username
    password = getpass('Please enter your school password: ')
    courseUrl = parse.urlparse(args.course_url)

    DOWNLOAD_DIR = parse.urlparse(args.download_dir).path
    # Append a forward slash if not provided
    if DOWNLOAD_DIR[-1] != '/':
        DOWNLOAD_DIR += '/'

    CANVAS_URL = "{0}://{1}".format(courseUrl.scheme, courseUrl.netloc)
    CANVAS_LOGIN_URL = CANVAS_URL + "/login/saml"

    # Get course id from url
    COURSE_ID = search('courses\/\d{4}', courseUrl.path)[0].split('/')[1]

    COURSE_URL = CANVAS_URL + "/courses/" + COURSE_ID 


    session = Session()

    print("Logging in...\n")
    login(username, password, session)
    print("Logged in successfully!")

    modules = get_modules(session)
    download_modules(modules, session)

    print("\nAll modules are downloaded to ", DOWNLOAD_DIR)

    

if  __name__ == '__main__':
    main()

