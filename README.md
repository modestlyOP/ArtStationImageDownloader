# ArtStationImageDownloader
This program scrapes images from a given ArtStation "Likes" Collections page (e.g. https://www.artstation.com/birdmech/collections/likes). ArtStation API limitations mean only the first 50 projects on the Likes collection page can be accessed. Video files are only saved as their corresponding thumbnail images. Existing files are not overwritten. Large numbers of images (100+) can cause problems like corrupted or incomplete files, as well as cause the downloader script to hang. (This project is an exercise in developing scraping scripts and learning basic software creation).

## To-do:
- Create a similar scraper script in python
- ~~Put a GUI over the script~~ (~~prompt username, storage path~~; display progress, ~~errors~~; ~~give option to download from a given project source~~)
- Upgrade GUI to Qt from Tk
- Figure out how to download video files as video

## DISCLAIMER:
This tool is for educational and personal non-profit use only! No AI is being trained with the downloaded images, nor are there plans to do this. Rather, the images obtained are for more easily inspiring other artists and/or providing them with curated reference art on demand and offline. A secondary purpose is archiving.

## WARNING:
Repeated runs of this script in short timeframes WILL cause you to be IP banned from ArtStation if downloading large numbers of files (250+)! Space out your runs acordingly!

## How To Run:
Simply run ``python [ASID_TTk.py or ASID_CTk.py] `` in command line (or just double-click that same file in Windows).

![image](https://github.com/modestlyOP/ArtStationImageDownloader/assets/48741294/a5113576-9f7c-4a44-b81a-32bb90c8bda2)
