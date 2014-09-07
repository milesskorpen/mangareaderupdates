# SETUP: pip install beautifulsoup4
# SETUP: pip install requests

#
# MANGA LIST
#

# Read in from MangaList.txt
# Format should be:
# NAME  MOST_RECENT
# If MOST_RECENT is blank, default to -1 (which means find any chapter)

import csv
import sys

manga_of_interest = {}

path_to_folder = "/Users/milesskorpen/projects/mangareaderupdates/" # UPDATE THIS

with open(path_to_folder+"MangaList.tsv","rw") as tsv:
    for line in csv.reader(tsv,delimiter="\t"):
        manga_of_interest[line[0]] = int(line[1])
        
#
# MAIN CODE
#

import requests
from bs4 import BeautifulSoup
from string import *

page = requests.get('http://www.mangareader.net/latest')
soup = BeautifulSoup(page.text)

url_list = []

for manga in soup.find_all("tr", "c2"):
    manga_series = []
    title = manga.find_all("a", "chapter")[0].get('href')
    
    # Clean the title
    # There might be two /s, in which case it is cached. Clean that shit.
    if title.count('/') > 1:
        # Cached; clean
        # First, remove the /###/ section
        second_slash = title.rfind("/")
        
        # Now, remove the .html and the slash
        title = title[second_slash+1:len(title)-5]
    else:
        # Just clean the starting /
        title = title[1:]
    
    # Is this a series I'm interested in?
    if title in manga_of_interest:
        
        most_recent_id = manga_of_interest[title]
        earliest_id = 1000000
        earliest_url = ""

        for chapter in manga.find_all("a", "chaptersrec"):
            chapter = chapter.get('href')
            
            # Get the chapter number
            # Cached; clean
            # First, remove the /###/ section
            second_slash = chapter.rfind("/")
            chapter_id = int(chapter[second_slash+1:])
            
            if chapter_id > manga_of_interest[title]:
                                
                if chapter_id > most_recent_id:
                    most_recent_id = chapter_id
                                
                if chapter_id < earliest_id:
                    earliest_id = chapter_id
                    earliest_url = "http://www.mangareader.net"+chapter
                    
        if earliest_url != "":
            url_list.append(earliest_url)
        
        manga_of_interest[title] = most_recent_id
        

    
# Export the MangaList.txt file

manga_list = []
for k,v in manga_of_interest.iteritems():
    manga_list.append([k,v])
    
with open(path_to_folder+'MangaList.tsv','wb') as f:
    writer = csv.writer(f,delimiter="\t")
    writer.writerows(manga_list)


# Show list of links
import os

file = path_to_folder+"MangaURLs.txt"
os.remove(file)

with open(file,'wb') as f:
    for item in url_list:
      f.write("%s\n" % item)