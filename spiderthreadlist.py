#!/usr/bin/env python3
import urllib.request
import sys
import json
import re
import codecs
import config

textreader = codecs.getreader("utf-8")
threadid = int(sys.argv[2])
threads = []
with open(sys.argv[1], mode="rt") as f:
    threadstext = f.readlines()
    for tidtext in threadstext:
        tidtext = tidtext.replace("\r", "").replace("\n", "")
        try:
            threads.append(int(tidtext))
        except (Exception):
            continue
    print("Found {0} threads in file.".format(len(threads)))

while threadid != 0:
    if threadid in threads:
        print("Chain is now linked again.")
        break
    thread = {}
    threads.append(threadid)
    print("Added thread {0}".format(threadid))
    try:
        newRequest = urllib.request.Request("{}/_/api/chan/post/?board=mlp&num={}".format(config.ARCHIVE_SITE, threadid))
        newRequest.add_header("user-agent", config.UA.format(vinfo=sys.version_info))
        thread = json.load(textreader(
            urllib.request.urlopen(newRequest)))
        if thread["comment"] is not None:
            previousthreadresults = re.findall("\\u003E\\u003E(\d+)", thread["comment"])
        else:
            previousthreadresults = []
        if len(previousthreadresults) > 0:
            print("Found {0} backlinks in OP, picking {1}".format(
                len(previousthreadresults), previousthreadresults[0]))
            threadid = int(previousthreadresults[0])
        else:
            print("Missing backlink in OP of thread {0}, please manually input a thread ID.".format(threadid))
            threadid = int(input("Thread ID: "))
    except BaseException as exc:
        print("------")
        print("An exception occured!")
        print("Content of JSON: {0}".format(thread.__repr__()))
        print("---")
        print("You can continue by manually retrieving the next thread, and")
        print("running with that. It will append to the files.")
        print("---")
        print("Stacktrace follows:")
        print("------")
        raise

with open(sys.argv[1], mode="wt") as f:
    for tid in threads:
        f.write("{0}\n".format(tid))

print("Exiting. Output is in {0}".format(sys.argv[1]))
