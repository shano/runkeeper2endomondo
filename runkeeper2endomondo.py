#!/usr/bin/env python
# encoding: utf-8
"""
runkeeper2endomondo.py

Licensed under MIT License.
Portions Copyright (c) 2013, Conor O'Neill <cwjoneill@gmail.com> - See http://conoroneill.net
Portions Copyright (c) 2012, Urban Skudnik <urban.skudnik@gmail.com> - See https://github.com/uskudnik/gpxjoin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

import sys
import os
from BeautifulSoup import BeautifulStoneSoup
import datetime
import glob

gpx_time_format = "%Y-%m-%dT%H:%M:%SZ"
sportstracker_time_format = "%Y-%m-%dT%H:%M:%S"

def main():

    files = list()

    for endomondo_file in glob.glob('./endomondo*.gpx'):
        os.remove(endomondo_file)

    # To make sure our data files are attached in correct order; we don't trust file system (download order, ...)
    for ffile in glob.glob('./*.gpx'):
        ffile = open(ffile, "r")
        filecontent = ffile.read()
        xml = BeautifulStoneSoup(filecontent)
        trkstart = xml.find("trk").find("time").string
        try:
            starttime = datetime.datetime.strptime(trkstart, gpx_time_format)
        except ValueError:
            # This deals with Sports Tracker files which have a silly time format
            index = trkstart.find('.')
            try:
                timepart = trkstart[0:index-1]
                starttime = datetime.datetime.strptime(timepart, sportstracker_time_format)
            except ValueError:
                # A user has submitted yet another Sports Tracker time format
                timepart = trkstart[0:index]
                starttime = datetime.datetime.strptime(timepart, sportstracker_time_format)
        files += [[starttime, filecontent]]

    input_ffiles = sorted(files, key=lambda *d: d[0])

    gpx_files_per_export = 50
    filecount = 0

    for ffiles in [input_ffiles[i:i+gpx_files_per_export] for i in range(0, len(input_ffiles), gpx_files_per_export)]:
        # GPX end tag is unnecessary from initial file
        joined_gpx = ffiles[0][1].split("</gpx>")[0]

        # "Header" data (initial xml tag, gpx tag, metadata, etc.) is unnecessary
        # in subsequent file, therefore we remove it, along with end GPX tag.
        for date, ffile in ffiles[1:]:
            header, content = ffile.split("<trk>")
            # Handle bug in runkeeper export that doesn't supply closing
            # </trkseg>
            if '</trkseg>' not in content:
                content = content.replace('</trk>', '</trkseg>\n</trk>')
            # Handle another bug where closing trackseg doesn't exist
            if "</trkpt>\n<trkseg>" in content:
                content = content.replace('</trkpt>\n<trkseg>', '</trkpt></trkseg>\n\n<trkseg>')


            content = "<trk>" + content
            joined_gpx += content.split("</gpx>")[0]

        # Processed all files, append end GPX tag
        joined_gpx += "</gpx>"

        # Write out concatenated file
        output_filename = "endomondo_%s.gpx" % filecount
        filecount += 1
        output_gpx = file(output_filename, "w")
        output_gpx.write(joined_gpx)
        output_gpx.close()

if __name__ == '__main__':
    main()

