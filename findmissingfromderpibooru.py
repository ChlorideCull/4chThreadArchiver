#!/usr/bin/env python3
# k[0]['5268501']['posts']['5381693']['media']['thumb_link']
import os
import sys
import codecs
import urllib.request
import urllib.error
import json
import shutil
import pickle

failedthreads = []
threads = []
primaryname = sys.argv[1]

token_find = '<input type="hidden" name="authenticity_token" value="'
path_find = '<h3><a href="'
dl_find = '<a rel="nofollow" title="View this image at full res with a short filename" href="'

textreader = codecs.getreader("utf-8")

print("Loading threads...")
if os.path.isfile(primaryname + "_thread_pickle"):
    print("  Found pickled save!")
    with open(primaryname + "_thread_pickle", mode="rb") as f:
        threads = pickle.load(f)
else:
    print("  Found no save. Run downloadthreaddata.py first.")
    exit(1)

print("Loading orphans...")
if os.path.isfile(primaryname + "_images_orphans.db.txt"):
    with open(primaryname + "_images_orphans.db.txt", mode="rt") as f:
        for line in f.readlines():
            line.replace("\r", "").replace("\n", "")
            data = line.split("\t")
            postid = data[1].split(",")[0][1:]
            print("  Working on hash '{0}' using thumbnail from {1}".format(data[0], postid))
            for thread in threads:
                rootkey = list(thread)[0]
                if rootkey == postid:
                    postid = "op"
                if "posts" not in thread[rootkey].keys():  # Fixes KeyError in threads without posts
                    thread[rootkey]["posts"] = {}
                thread[rootkey]["posts"]["op"] = thread[rootkey]["op"]  # For simpler parsing, place op post in the rest of em
                for post in thread[rootkey]["posts"]:
                    if post == postid:
                        thumburl = thread[rootkey]["posts"][post]['media']['thumb_link']
                        print("    Thumbnail is at '{0}'".format(thumburl))
                        #authtokenpage = textreader(urllib.request.urlopen(url="https://derpiboo.ru/search/reverse")).read();
                        #authtokenorigin = authtokenpage.find(token_find)
                        #authtoken = authtokenpage[authtokenorigin:authtokenorigin+88][len(token_find):]
                        #print("    Using AuthToken {0}".format(authtoken))
                        responsepage = textreader(urllib.request.urlopen(urllib.request.Request("https://derpiboo.ru/search/reverse",
                                                data=("--BoundAss" + "\r\n" +
                                                    'Content-Disposition: form-data; name="url"' + "\r\n" +
                                                    "\r\n" +
                                                    thumburl + "\r\n" +
                                                    "--BoundAss--").encode(),
                            headers={
                                "Host": "derpiboo.ru",
                                "User-Agent": "Cull Bot (Python 3.x)",
                                "Cache-Control": "no-cache",
                                "Accept": "*/*",
                                "Content-Type": "multipart/form-data; boundary=BoundAss"
                        }))).read()
                        imageidorigin = responsepage.find(path_find)
                        if imageidorigin < 0:
                            print("    Did not find image on Derpibooru.")
                            continue
                        imageid = responsepage[imageidorigin:imageidorigin+25][len(path_find):].split('"')[0]
                        imagepage = textreader(urllib.request.urlopen(url="https://derpiboo.ru" + imageid)).read();
                        dllinkorigin = imagepage.find(dl_find)
                        if dllinkorigin < 0:
                            print("    Fucked up parsing. Go yell at the dev.")
                            continue
                        dllink = imagepage[dllinkorigin:dllinkorigin+len(dl_find)+54][len(dl_find):].split('"')[0]
                        print("    Download link is '{0}'.".format(dllink))
                        with open("{0}_images/{1}".format(primaryname, thread[rootkey]["posts"][post]["media"]["media"]), mode="wb") as of:
                            shutil.copyfileobj(urllib.request.urlopen(url="https:" + dllink), of)
                        print("    Finished downloading as '{0}'.".format("{0}_images/{1}".format(primaryname, thread[rootkey]["posts"][post]["media"]["media"])))
else:
    print("  Found no orphans. Either the archive was #togood or you haven't run archiveimages.py yet.")
    exit(1)