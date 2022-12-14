#!/usr/bin/env python3
import argparse
import os
from time import time 

conf = {}

def isGrafanaIndexFilePatched(grafanaIndexFilePath, customCSSFilePath):
    print ("Checking if the index file is patched already...")
    with open(grafanaIndexFilePath, 'r') as file:
        data = file.read()
        if ']]%s"/>'%customCSSFilePath in data:
            return True
        else:
            return False

def patchGrafanaIndexFile(grafanaIndexFilePath, grafanaTheme, customCSSFilePath):
    print ("Patching the grafana index file %s to load the custom css file %s..."%(grafanaIndexFilePath,customCSSFilePath))
    if not isGrafanaIndexFilePatched(grafanaIndexFilePath, customCSSFilePath):
        newData = None
        with open(grafanaIndexFilePath, 'r') as file:
            data = file.read()
            #</style><div class="preloader">
            idx = data.index('<div class="preloader">')
            newData = data[0:idx]
            newData += '[[ if eq .Theme "'+grafanaTheme+'" ]]<link rel="stylesheet" href="[[.ContentDeliveryURL]]%s"/>[[ end ]]' % (customCSSFilePath)
            newData += data[idx:]
        
        with open(grafanaIndexFilePath, 'w') as file:
            file.write(newData)
        

        return True
    else:
        print ("Skipping as it is already patched!")
        return False


parser = argparse.ArgumentParser(
    prog = 'Grafana custom CSS patch',
    description = 'Adds a custom css file at the bottom of the index file of Grafana installations.'
    )

parser.add_argument('-c', '--css', dest="cssSourceFile", default="custom-css/custom.css")
parser.add_argument('-d', '--directory', dest='grafanaRootDir', default="/usr/share/grafana")
parser.add_argument('-t', '--theme', dest='grafanaTheme', default="light")

args = parser.parse_args()

conf["grafanaRootDir"] = args.grafanaRootDir
conf["grafanaIndexFilePath"] = os.path.join(conf["grafanaRootDir"], "public", "views","index.html")
conf["grafanaTheme"] = args.grafanaTheme
conf["customCSSDir"] = os.path.join("public", "custom-css")
conf["cssSourceFile"] = args.cssSourceFile
conf["customCssFilename"] = os.path.basename(conf["cssSourceFile"])
conf["customCssFile"] = os.path.join(conf["customCSSDir"], conf["customCssFilename"])

print ("Patching the grafana index file if needed...")
patchGrafanaIndexFile(conf["grafanaIndexFilePath"], conf["grafanaTheme"], conf["customCssFile"])
print ("Patching done.")
