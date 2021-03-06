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

highestpickledthread = 0
failedthreads = []
threads = []
primaryname = sys.argv[1] + "_threads"
board = sys.argv[2]

textreader = codecs.getreader("utf-8")

print("Loading threads...")
if os.path.isfile(primaryname + "_thread_pickle"):
    print("  Found previous save! Ignoring everything older than the newest in pickled save.")
    with open(primaryname + "_thread_pickle", mode="rb") as f:
        threads = pickle.load(f)
        for thread in threads:
            if int(list(thread)[0]) > highestpickledthread:
                highestpickledthread = int(list(thread)[0])
else:
    print("  Found no save. Preparing folders.")
    os.mkdir(primaryname + "_images")
    
with open(primaryname, mode="rt") as f:
    threadids = f.readlines()
    i = 0
    for line in threadids:
        i += 1
        line = line.replace("\r", "").replace("\n", "")
        if line == "":
            continue
        sys.stdout.write("\r  Thread {0}/{1} - {2}".format(i, len(threadids), line))
        if (highestpickledthread != 0) and (int(line) < highestpickledthread):
            continue
        error = 0
        docont = False
        while (error < 3) and not docont:
            try:
                docont = True
                newRequest = urllib.request.Request("{}/_/api/chan/thread/?board={}&num={}".format(config.ARCHIVE_SITE, board, line))
                newRequest.add_header("user-agent", config.UA.format(vinfo=sys.version_info))
                jsonresp = json.load(textreader(
                    urllib.request.urlopen(newRequest)))
                if "error" in jsonresp.keys():
                    print("")
                    print("    Server error occurred: {0}".format(jsonresp["error"].__repr__()))
                    docont = False
                    error += 1
                else:
                    if int(line) == highestpickledthread:
                        threads = threads[:-1]
                    threads.append(jsonresp)
            except Exception as e:
                print("")
                print("    Error occurred: {0}".format(e.__repr__()))
                docont = False
                error += 1
        if not docont:
            failedthreads.append(line)

print("")
print("  Saving thread object...")
with open(primaryname + "_thread_pickle", mode="wb") as f:
    pickle.dump(threads, f, protocol=pickle.HIGHEST_PROTOCOL)

if len(failedthreads) > 0:
    print("WARNING: The following threads failed to load:")
    for fail in failedthreads:
        print(" * {0}".format(fail))
else:
    print("No threads failed to load.")