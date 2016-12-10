#!/usr/bin/python3

import exifread
import argparse
import os
from bs4 import BeautifulSoup
from io import BytesIO
import urllib, urllib.request, urllib.error
import requests

def getArgs():
    parser = argparse.ArgumentParser(description='Check for geotagged images or scrape the web for them')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', action='store', metavar='Filename', nargs='+', help='Point to an image file to check for geotags')
    group.add_argument('-u', action='store', metavar='URL', help='URL for scraping')
    args = parser.parse_args()
    return args

def openImg(img):
    return open(img, 'rb')

def convertCoords(coords):
    coords = coords.replace('[', '').replace(']', '')
    coords = coords.split(',')
    coords[2] = eval(coords[2])
    coords = [ float(val) for val in coords ]
    coords = coords[0] + coords[1] / 60 + coords[2] / 3600
    return(round(coords, 6))

def getExif(image):
    exif = exifread.process_file(image)
    if not exif:
        raise Exception('No exif data')
    if 'GPS GPSLatitude' not in exif:
        raise Exception('No GPS data')
    gpsInfo = [exif['GPS GPSLatitude'], exif['GPS GPSLatitudeRef'], exif['GPS GPSLongitude'], exif['GPS GPSLongitudeRef'],
            exif['GPS GPSMapDatum']]
    gpsInfo = [ str(val) for val in gpsInfo ]
    gpsInfo[0] = convertCoords(gpsInfo[0])
    gpsInfo[2] = convertCoords(gpsInfo[2])
    return gpsInfo

def getURL(url):
    return urllib.request.urlopen(url).read()

def downloadImgMem(imgURL):
    img = requests.get(imgURL)
    return BytesIO(img.content)

def main():
    args = getArgs()
#    print(args)
    if args.f:
        for imgFile in args.f:
            if not os.path.isfile(imgFile):
                raise Exception('File does not exist')
                continue
            img = openImg(imgFile)
            try:
                print(imgFile + ',', getExif(img))
            except Exception:
                print(imgFile + ',', 'No data')
            img.close()
    if args.u:
        soup = BeautifulSoup(getURL(args.u), 'lxml')
        for img in soup.select('img'):
            try:
                if img['src'][0:4] == 'http':
                    fullURL = img['src']
                else:
                    URL = (args.u, img['src'])
                    fullURL = ''.join(URL)
                print(img['src'])
                memImg = downloadImgMem(fullURL)
                try:
                    print(getExif(memImg))
                except Exception:
                    continue
            except urllib.error.HTTPError:
                print('Scraped image returned HTTP error')
            

if __name__ == '__main__':
    main()

#todo list
#
#kml output
#add datetimeoriginal
#check filetype
#add random useragent strings
#fix mem stuff
