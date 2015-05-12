from bs4 import BeautifulSoup
import os
import urllib
import urllib2
import sys
import time
import datetime

now = datetime.datetime.now()

print now
#print now.year
#print now.month
#print now.day
#print now.hour
#print now.minute
#print now.second

#day_delta = 1
#datetime_to_read = now - datetime.timedelta(days=day_delta)
#date = str(datetime_to_read).split()
#print "1 day ago was: ", now - datetime.timedelta(days=day_delta)

sys.setrecursionlimit(2000)
 
#Open a file for writing/appending 
f = open("dilbertstripsall.txt","a")
f.truncate()

#define function to retrieve Dilbert comic-of-the-day content
def getDilbertContent(dateofcomic):
  print "http://dilbert.com/strip/" + dateofcomic
  try:
    #Load the content from the Dilbert comic url into a BeautifulSoup object
    # Dilbert.com has individual strips with the date at the end of the URL
    url = urllib2.urlopen("http://dilbert.com/strip/" + dateofcomic)
    content = url.read()
 
    soup = BeautifulSoup(content)
 
    #Looking for all the "div" tags
    dilbertText = soup.find_all("div")
    #Dilbert dialogue is contained in the the 8th div tag
    #Extract the comic strip date and the accompanying dialogue
    print str(dilbertText[10].get('data-id'))
    comic_date = str(dilbertText[10].get('data-id'))
    print str(dilbertText[10].get('data-description'))

    f.write(str(dilbertText[10].get('data-id')) + " * ")
    f.write(str(dilbertText[10].get('data-description')) + "\n")
    print "Done with script " + dateofcomic

    imgs = soup.findAll("div", {"class":"img-comic-container"})    
    for img in imgs:
        imgUrl = img.img['src'].split("src")[0]
        print str(imgUrl)
        # urllib.urlretrieve(imgUrl, os.path.basename(imgUrl)+".gif")
        urllib.urlretrieve(imgUrl, os.path.basename(comic_date)+".gif")
    
  except:
    print "Unable to open script " + dateofcomic




# Iterate through loop to go through past comic strips
for i in range(1,9465):
  #Get the current date minus the number of days in the loop iteration
  datetime_to_read = now - datetime.timedelta(days=i)
  #Split up the date/time components
  date = str(datetime_to_read).split()
  # Just get the YYYY-MM-DD
  print date[0]
  # call function to read Dilbert comic strip URL for a given day
  getDilbertContent(str(date[0]))
  # pause 1200 msec
  time.sleep(1.2) 

  f.close

