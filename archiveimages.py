#!/usr/bin/env python3

# 4chThreadArchiver
# Copyright (C) 2016, Sebastian "Chloride Cull" Johansson
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

import os
import sys
import codecs
import urllib.request
import urllib.error
import shutil
import pickle
import config


dofullrescan = False
highestpickledthread = 0
failedthreads = []
threads = []
imagemap = {}
imagepostmap = {}
orphanimagemaps = {}
primaryname = sys.argv[1] + "_threads"

textreader = codecs.getreader("utf-8")

print("Loading threads...")
if os.path.isfile(primaryname + "_thread_pickle"):
    print("  Found pickled save!")
    with open(primaryname + "_thread_pickle", mode="rb") as f:
        threads = pickle.load(f)
        for thread in threads:
            if int(list(thread)[0]) > highestpickledthread:
                highestpickledthread = int(list(thread)[0])
else:
    print("  Found no save. Run downloadthreaddata.py first.")
    exit(1)

print("Generating image-post map...")
if (os.path.isfile(primaryname + "_imagepostmap_pickle")) and (highestpickledthread > 0):
    print("  Found pickled backup! Loading.")
    with open(primaryname + "_imagepostmap_pickle", mode="rb") as f:
        imagepostmap = pickle.load(f)
    if os.path.isfile(primaryname + "_orphanimagemap_pickle"):
        with open(primaryname + "_orphanimagemap_pickle", mode="rb") as f:
            orphanimagemaps = pickle.load(f)
else:
    print("  Found no backup.")

for thread in threads:
    rootkey = list(thread)[0]
    print("  Working on thread {0}".format(rootkey))
    if "posts" not in thread[rootkey].keys():  # Fixes KeyError in threads without posts
        thread[rootkey]["posts"] = {}
    thread[rootkey]["posts"]["op"] = thread[rootkey]["op"]  # For simpler parsing, place op post in the rest of em
    for post in thread[rootkey]["posts"]:
        post = thread[rootkey]["posts"][post]
        if post["media"] is not None:
            imagehash = post["media"]["media_hash"]
            if imagehash in imagepostmap.keys():
                if int(post["num"]) not in imagepostmap[imagehash]: #Solves a weird duplication issue
                    imagepostmap[imagehash].append(int(post["num"]))
                print("    Image '{0}' already in DB, associating post.".format(imagehash))
            else:
                print("    Image '{0}' added to DB.".format(imagehash))
                imagepostmap[imagehash] = [int(post["num"])]

print("  Backing up map object...")
with open(primaryname + "_imagepostmap_pickle", mode="wb") as f:
    pickle.dump(imagepostmap, f, protocol=pickle.HIGHEST_PROTOCOL)


print("Archiving all images...")
for thread in threads:
    rootkey = list(thread)[0]
    print("  Archiving images from thread {0}".format(rootkey))
    if "posts" not in thread[rootkey].keys():  # Fixes KeyError in threads without posts
        thread[rootkey]["posts"] = {}
    thread[rootkey]["posts"]["op"] = thread[rootkey]["op"]  # For simpler parsing, place op post in the rest of em
    for post in thread[rootkey]["posts"]:
        post = thread[rootkey]["posts"][post]
        if post["media"] is not None:
            imagehash = post["media"]["media_hash"]
            if imagehash in imagemap.keys():
                print("    Image '{0}' already stored, skipping..".format(imagehash))
            else:
                print("    Image '{0}' downloading...".format(imagehash))
                if os.path.isfile(primaryname + "_images/" + post["media"]["media"]):
                    print("      Already downloaded, just adding to store.")
                    imagemap[imagehash] = post["media"]["media"]
                elif (not dofullrescan) and (imagehash in orphanimagemaps.keys()) and (int(post["num"]) in orphanimagemaps[imagehash]):
                    print("      Previously failed download. Ignoring.")
                    continue
                else:
                    urlfile = None
                    try:
                        newRequest = urllib.request.Request(post["media"]["media_link"])
                        newRequest.add_header("user-agent", config.UA.format(vinfo=sys.version_info))
                        urlfile = urllib.request.urlopen(newRequest)
                    except urllib.error.URLError:
                        print("      Failed to download image.")
                        continue
                    with open(primaryname + "_images/" + post["media"]["media"], mode="wb") as imgf:
                            shutil.copyfileobj(urlfile, imgf)
                            print("      Saved!")
                            imagemap[imagehash] = post["media"]["media"]


print("Writing combined database information...")
with open(primaryname + "_images.db.txt", mode="wt") as f:
    orphanimagemaps = {}
    for image in imagepostmap.keys():
        if image not in imagemap.keys():
            # print("  Hash '{0}' lacks an image - flagged as orphan.".format(image))
            orphanimagemaps[image] = imagepostmap[image]
            continue
        tmpstr = ""
        for post in imagepostmap[image]:
            tmpstr += str(post) + ","
        f.write("{0}\t{1}\t{2}\n".format(imagemap[image], len(imagepostmap[image]), tmpstr))

if len(orphanimagemaps) > 0:
    print("WARNING: There are still orphans. Writing list to {0}".format(primaryname + "_images_orphans.db.txt"))
    with open(primaryname + "_images_orphans.db.txt", mode="wt") as f:
        for image in orphanimagemaps.keys():
            tmpstr = ""
            for post in orphanimagemaps[image]:
                tmpstr += str(post) + ","
            f.write("{0}\t{1}\n".format(image, orphanimagemaps[image]))
    with open(primaryname + "_orphanimagemap_pickle", mode="wb") as f:
        pickle.dump(orphanimagemaps, f, protocol=pickle.HIGHEST_PROTOCOL)
else:
    print("No orphans found. Data is clean.")
