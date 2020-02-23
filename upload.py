#!/usr/bin/env python

"""
Uploads all .bw and junctions.bed files to genome browser and
generates links to view them in the UCSC browser.

NOTE: The lftp_upload.sh script must be present in the same
directory.

NOTE: If lftp is being unresponsive, try the script again
after 2-3 minutes. This is usegalaxy.org throttling against
DDoS atacks.

NOTE: files uploaded to galaxy FTP are deleted after 3 days.
"""

import glob
import argparse
import getpass
from ftplib import FTP_TLS
import os

import ssl
import ftplib
from ftplib import FTP
from ftplib import FTP_TLS

import subprocess as sp

from bioblend import galaxy

# Explicit FTPS with shared TLS session
class FTPS_connect(FTP_TLS):

  def ntransfercmd(self, cmd, rest=None):
      conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
      if self._prot_p:
          session = self.sock.session
          if isinstance(self.sock, ssl.SSLSocket):
                  session = self.sock.session
          conn = self.context.wrap_socket(conn,
                                          server_hostname=self.host,
                                          session=session) 
      return conn, size

track_str_bw = "track name=%s description=%s type=bigWig visibility=2 db=hg38 bigDataUrl=https://usegalaxy.org/datasets/%s/display?to_ext=txt\n"
track_str_bed = "track name=%s description=%s visibility=2 db=hg38 useScore=1"
ucsc_str = "http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&hgct_customText=https://usegalaxy.org/datasets/%s/display?to_ext=txt"

bwfiles   = {}

# Define script arguments.
parser = argparse.ArgumentParser(
    description="Uploads all .bw files in dir to genome browser and generates links to view them in the UCSC browser.",
    epilog="Usage eg: ./upload.py fadhil@cmu.edu d1e32 /home/data/bigwig_dir experiment-1")

parser.add_argument("username", help="Username for usegalaxy.org.")
parser.add_argument("api_key",  help="API key obtained from usegalaxy.org.")
parser.add_argument("dir",   help="Directory of bigWig and junctions.bed files to upload.")
parser.add_argument("proj_name",help="Name to give track file. Existing track files with same name will be overwritten.")

args = parser.parse_args()

print (">>> Enter FTP password below.")
password = getpass.getpass()

# # Open a galaxy instance using the api key.
gi = galaxy.GalaxyInstance(url='usegalaxy.org', key=args.api_key)
histid = gi.histories.get_most_recently_used_history()["id"]

# First upload all .bw files to the galaxy FTP server.
print(">>> Uploading .bw files to FTP server.")

# Set up FTPS connection
ftps = FTPS_connect (host='129.114.60.56', user=args.username, passwd=password)
ftps.set_debuglevel(10)
ftps.prot_p()
ftps.retrlines('LIST')

# Upload all .bw filenames to the galaxy FTP server.
for filename in (glob.glob(args.dir+"/*.bw")):
    f = open(filename, 'rb')
    cmd = 'STOR '+filename
    ftps.storbinary (cmd, f)

ftps.close()

# Store all .bw filenames into a dict for easy access later.
# glob returns a list, so this works nicely.
for f in (glob.glob(args.dir + "/*.bw")):
    bwname = f.split("/")[-1]
    bwfiles[bwname] = 1

track_filename = args.proj_name + ".txt"
track_file = open(track_filename, "w+")
track_file.write("browser hide all \nbrowser full ruler \nbrowser pack refGene knownGene \n")

# Push .bw file on FTP server to history and
# attach .bw links to track_file.
for f in gi.ftpfiles.get_ftp_files():
    if f["path"] in bwfiles:
        print (">>> Moving %s to default history." % f["path"])
        r = gi.tools.upload_from_ftp(f["path"], histid)

        track_file.write(track_str_bw % (f["path"], f["path"], r["outputs"][0]["id"]))

        print (">>> Added line to track file.\n")

# Append any .bed data to the end of the track file.
for f in glob.glob(args.dir + "/*.bed"):
    print (">>> Appending %s to track_file." % f)
    track_file.write("browser hide all \nbrowser full ruler \nbrowser pack refGene knownGene \n")
    track_file.write(track_str_bed % (f.split("/")[-1], f.split("/")[-1]) + "\n")
    track_file.write(open(f).read())
    
track_file.close()

print (">>> Uploading track file to FTP and generating link...")

p = sp.call(["lftp", "-c", "open -u %s,%s usegalaxy.org; put %s" % (args.username, password, track_filename)])

# Get track_file url from FTP server.
for f in gi.ftpfiles.get_ftp_files():
    if f["path"] == track_filename:
        print (">>> Moving track-file to default history.")
        r = gi.tools.upload_from_ftp(f["path"], histid)
        url = r["outputs"][0]["id"]
        break

f = open(args.proj_name + "_URL.txt", "w+")
f.write((ucsc_str % url).strip())
f.close()
print (">>> Track file url saved to %s.url\n" % args.proj_name)
print (">>> Bye and come again!")
