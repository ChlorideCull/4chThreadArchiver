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

import sys

threadlists = []

for arg in sys.argv:
    if arg == sys.argv[0]:
        continue
    with open(arg, mode="rt") as f:
        currentlist = []
        outputlist = []
        for line in f.readlines():
            line.replace("\r", "").replace("\n", "")
            if line != "":
                currentlist.append(int(line))
        if len(threadlists) > 0:
            for tlist in threadlists:
                for threadid in currentlist:
                    if threadid not in tlist:
                        outputlist.append(threadid)
            print("{0} uniques in {1}".format(len(outputlist), arg))
        else:
            print("Using {0} as base list".format(arg))
            outputlist = currentlist
        threadlists.append(outputlist)
print("Preparing output...")
finaloutput = []
for tlist in threadlists:
    for tlistitem in tlist:
        finaloutput.append(tlistitem)
print("Sorting output...")
finaloutput.sort()
print("Writing to disk...")
with open(sys.argv[1] + "_merged", mode="wt") as f:
    for item in finaloutput:
        f.write(str(item) + "\n")
print("Merged output is named {0}_merged, and has {1} threads.".format(sys.argv[1], len(finaloutput)))
