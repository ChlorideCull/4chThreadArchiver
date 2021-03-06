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
import pickle


dofullrescan = False
threads = []
imagepostmap = {}

imagehashes = []
primaryname = sys.argv[1]
artistname = sys.argv[2]

textreader = codecs.getreader("utf-8")

print("Loading threads...")
if os.path.isfile(primaryname + "_thread_pickle"):
    print("  Found pickled save!")
    with open(primaryname + "_thread_pickle", mode="rb") as f:
        threads = pickle.load(f)
else:
    print("  Found no save. Run downloadthreaddata.py first.")
    exit(1)

print("Loading image map...")
if os.path.isfile(primaryname + "_imagepostmap_pickle"):
    print("  Found pickled save!")
    with open(primaryname + "_imagepostmap_pickle", mode="rb") as f:
        imagepostmap = pickle.load(f)
else:
    print("  Found no save. Run archiveimages.py first.")
    exit(1)

print("Finding posts by {0}".format(artistname))
for thread in threads:
    rootkey = list(thread)[0]
    print("  Working on thread {0}".format(rootkey))
    if "posts" not in thread[rootkey].keys():  # Fixes KeyError in threads without posts
        thread[rootkey]["posts"] = {}
    thread[rootkey]["posts"]["op"] = thread[rootkey]["op"]  # For simpler parsing, place op post in the rest of em
    for post in thread[rootkey]["posts"]:
        post = thread[rootkey]["posts"][post]
        if (post["name"] == artistname) or (artistname == "?"):
            if post["media"] is not None:
                if post["media"]["media_hash"] not in imagehashes:
                    imagehashes.append(post["media"]["media_hash"])
print("{0} images posted by {1}".format(len(imagehashes), artistname))
print("Finding most popular images...")
outputmap = {}
for item in imagepostmap:
    tmp = []
    for etem in imagepostmap[item]:
        if etem not in tmp:
            tmp.append(etem)
    imagepostmap[item] = tmp
count = 0
for item in sorted(imagehashes, key=lambda x: len(imagepostmap[x]), reverse=True):
    if count < 10:
        count += 1
        print("  '{0}' found in '{1}' has {2} reposts.".format(item, imagepostmap[item][0], len(imagepostmap[item])))
