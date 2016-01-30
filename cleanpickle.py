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
import json
import pickle
import config
import shutil

primaryname = sys.argv[1]

threads = None
confirmed_dupes = []
dupe_winner_list = []

print("Loading threads...")
if os.path.isfile(primaryname + "_thread_pickle"):
    print("  Found previous save! Prepping clean.")
    with open(primaryname + "_thread_pickle", mode="rb") as f:
        threads = pickle.load(f)
else:
    print("  Found no save. You must have a dirty pickle to clean it!")
    exit(1)
print("Cleaning!")
print(" Deduplication!")
for i in range(0, len(threads)):
    i_had_dupe = False
    for k in range(i+1, len(threads)):
        if k in confirmed_dupes:
            continue
        if list(threads[i])[0] == list(threads[k])[0]:
            confirmed_dupes.append(k)
            i_had_dupe = True
    if i_had_dupe:
        confirmed_dupes.append(i)

print("  Found {} dupes.".format(len(confirmed_dupes)))
for i in confirmed_dupes:
    already_dedup = False
    for j in dupe_winner_list:
        if list(threads[j])[0] == list(threads[i])[0]:
            already_dedup = True
            break
    if already_dedup:
        continue
    biggest_thread_save = len(threads[i][list(threads[i])[0]]["posts"])
    biggest_thread_save_id = i
    for k in confirmed_dupes:
        if i == k:
            continue
        if list(threads[i])[0] == list(threads[k])[0]:
            savesize = len(threads[k][list(threads[k])[0]]["posts"])
            if savesize > biggest_thread_save:
                print("   {} ({}) was bigger than {} ({}).".format(k, savesize, biggest_thread_save_id, biggest_thread_save))
                biggest_thread_save = savesize
                biggest_thread_save_id = k
            else:
                print("   {} ({}) was smaller than, or the same size as, {} ({}).".format(k, savesize, biggest_thread_save_id, biggest_thread_save))
    print("   {} ({}) wins.".format(biggest_thread_save_id, biggest_thread_save))
    dupe_winner_list.append(biggest_thread_save_id)
print("  To preserve: {}".format(dupe_winner_list))
delete_list = [x for x in confirmed_dupes if x not in dupe_winner_list]
print("  To delete:   {}".format(delete_list))
print(" Updating memory thread object...")
threads = [threads[x] for x in range(0, len(threads)) if x not in delete_list]
print(" Backing up original pickle...")
shutil.copy2(primaryname + "_thread_pickle", primaryname + "_thread_pickle.bak")
print(" Saving pickle...")
with open(primaryname + "_thread_pickle", mode="wb") as f:
    pickle.dump(threads, f, protocol=pickle.HIGHEST_PROTOCOL)
print("Done!")
