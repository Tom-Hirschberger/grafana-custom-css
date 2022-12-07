#!/usr/bin/env python3
import argparse
import os
import shutil
import pprint
import subprocess
import sys
import glob
from time import time 

conf = {}
conf["scriptPath"] = __file__
conf["scriptDir"] = os.path.normpath(os.path.dirname(__file__))
conf["serviceTemplatePath"] = os.path.join(conf["scriptDir"], "service.template")
conf["systemdPath"] = "/etc/systemd/system"
conf["patchServiceName"] = "grafana-custom-css.service"
conf["backupExtension"] = ".org.customCss"

if os.geteuid() != 0:
    print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    sys.exit(1)

def isPatchServiceRegistered(patchServiceName):
    output = subprocess.run(["systemctl", "list-units", "--type=service", "--no-pager"], shell=False, capture_output=True)
    services = output.stdout.decode("utf-8").split('\n')
    name = None
    for service in services:
        service = service.strip()
        if len(service) > 0:
            name = service.split()[0]
            if name is patchServiceName:
                return True
    
    return False

def removeSystemService(patchServiceName, patchServiceFilePath):
    print ("Removing system service %s and its service file %s..."%(patchServiceName, patchServiceFilePath))
    if isPatchServiceRegistered(patchServiceName):
        subprocess.run(["systemctl", "--no-pager", "stop", patchServiceName], shell=False)
        subprocess.run(["systemctl", "--no-pager", "disable", patchServiceName], shell=False)
    
    if os.path.exists(patchServiceFilePath):
        os.remove(patchServiceFilePath)
        return True
    else:
        return False


def registerSystemService(patchScriptPath, patchServiceName, patchServiceFilePath, templateFilePath, grafanaServiceName, grafanaRootDir, grafanaTheme ,cssFilePath):
    print("Trying to register system service...")
    if isPatchServiceRegistered(patchServiceName):
        print("Service %s is registered already. Removing old one first!" % patchServiceName)
        removeSystemService(patchServiceName, patchServiceFilePath)
    
    with open(templateFilePath, 'r') as file:
        print("Creating new service file %s as of template file %s..." %(patchServiceFilePath, templateFilePath))
        data = file.read()
        data = data.replace("###GRAFANA_SERVICE###", grafanaServiceName)
        data = data.replace("###PATCH_SCRIPT_PATH###", patchScriptPath)
        data = data.replace("###GRAFANA_DIR###", grafanaRootDir)
        data = data.replace("###CSS_FILE###", cssFilePath)
        data = data.replace("###THEME###", grafanaTheme)

        with open(patchServiceFilePath, 'w') as serviceFile:
            serviceFile.write(data)
        
        print("Enable and starting the new service %s..." % patchServiceName)
        subprocess.run(["systemctl", "--no-pager", "enable" , patchServiceName], shell=False)
        subprocess.run(["systemctl", "--no-pager", "start", patchServiceName], shell=False)



def determineGrafanaServiceName(patchServiceName):
    print("Checking whats the name of of the grafana service...")
    output = subprocess.run(["systemctl", "--no-pager", "list-units", "--type=service"], shell=False, capture_output=True)
    services = output.stdout.decode("utf-8").split('\n')

    name = None
    for service in services:
        name = service.strip()
        if len(name) > 0:
            name = name.split()[0]
            if (not name is patchServiceName) and ("grafana" in name):
                break
            else:
                name = None
        else:
            name = None
    
    if name != None:
        return name
    else:
        print ("WARN: Could not determine grafana service. Using default: grafana-server.service!")
        return "grafana-server.service"

def determineGrafanaDirectory():
    print("Checking where the root directory of grafana is...")
    return "/usr/share/grafana"

def prepareCustomCSSDir(grafanaRootDir, customCSSDir, cssSourceFilePath, cssDestFileName):
    print("Preparing custom css destination directory...")
    customCSSDirAbsPath = os.path.join(grafanaRootDir, customCSSDir)
    if not os.path.exists(customCSSDirAbsPath):
        print("Creating directory: %s" % customCSSDirAbsPath)
        os.makedirs(customCSSDirAbsPath)
    
    customCSSFilePath = os.path.join(customCSSDirAbsPath, cssDestFileName)
    
    print("Copy %s to %s" % (cssSourceFilePath, customCSSFilePath))
    shutil.copyfile(cssSourceFilePath,customCSSFilePath)

def removeCustomCSSDir(grafanaRootDir, customCSSDir):
    if customCSSDir != "":
        customCSSPath = os.path.join(grafanaRootDir, customCSSDir)
        if (os.path.exists(customCSSPath)):
            shutil.rmtree(customCSSPath)
            return True
        else:
            return False
    else:
        return False

def isGrafanaIndexFilePatched(grafanaIndexFilePath, customCSSFilePath):
    print ("Checking if the index file is patched already...")
    with open(grafanaIndexFilePath, 'r') as file:
        data = file.read()
        if ']]%s"/>'%customCSSFilePath in data:
            return True
        else:
            return False

def patchGrafanaIndexFile(grafanaIndexFilePath, backupExtension, grafanaTheme, customCSSFilePath):
    print ("Patching the grafana index file %s to load the custom css file %s..."%(grafanaIndexFilePath,customCSSFilePath))
    if not isGrafanaIndexFilePatched(grafanaIndexFilePath, customCSSFilePath):
        backupGrafanaIndexFile(grafanaIndexFilePath, backupExtension)
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

def backupGrafanaIndexFile(grafanaIndexFilePath, backupExtension):
    backupFile = grafanaIndexFilePath+backupExtension
    if os.path.exists(backupFile):
        backupFile = backupFile+".%d"%time()

    print ("Backup the original index file to path %s" % backupFile)

    shutil.copyfile(grafanaIndexFilePath,backupFile)
    return False

def restoreGrafanaIndexFile(grafanaIndexFilePath, backupExtension):
    backupFile = grafanaIndexFilePath+backupExtension
    print("Trying to restore original grafana index file of backup %s..."%backupFile)
    if os.path.exists(backupFile):
        shutil.copyfile(backupFile, grafanaIndexFilePath)
        return True 
    return False

def removeGrafanaIndexBackupFiles(grafanaIndexFilePath, backupExtension):
    backupFile = grafanaIndexFilePath+backupExtension
    if os.path.exists(backupFile):
        print ("Removing file %s."%backupFile)
        os.remove(backupFile)
    fileList = glob.glob(grafanaIndexFilePath+backupExtension+'.*')
    for filePath in fileList:
        print ("Removing file %s."%filePath)
        os.remove(filePath)


parser = argparse.ArgumentParser(
    prog = 'Grafana custom CSS patch',
    description = 'Adds a custom css file at the bottom of the index file of Grafana installations.'
    )

parser.add_argument('-c', '--css', dest="cssSourceFile", default=os.path.join(conf["scriptDir"], "mystyle.css"))
parser.add_argument('-d', '--directory', dest='grafanaRootDir', default=determineGrafanaDirectory())
parser.add_argument('-s', '--service', dest='grafanaServiceName', default=determineGrafanaServiceName(conf["patchServiceName"]))
parser.add_argument('-t', '--theme', dest='grafanaTheme', default="light")
parser.add_argument('-r', '--register', action='store_true', dest="register", default=False)
parser.add_argument('-u', '--undo', action='store_true', dest="undo", default=False)

args = parser.parse_args()

conf["grafanaRootDir"] = args.grafanaRootDir
conf["grafanaServiceName"] = args.grafanaServiceName
conf["grafanaIndexFilePath"] = os.path.join(conf["grafanaRootDir"], "public", "views","index.html")
conf["grafanaTheme"] = args.grafanaTheme
conf["customCSSDir"] = os.path.join("public", "custom-css")
conf["cssSourceFile"] = args.cssSourceFile
conf["customCssFilename"] = os.path.basename(conf["cssSourceFile"])
conf["customCssFile"] = os.path.join(conf["customCSSDir"], conf["customCssFilename"])

if args.register:
    print ("Register the service...")
    prepareCustomCSSDir(conf["grafanaRootDir"], conf["customCSSDir"], conf["cssSourceFile"], conf["customCssFilename"])
    registerSystemService(conf["scriptPath"], conf["patchServiceName"], os.path.join(conf["systemdPath"], conf["patchServiceName"]), conf["serviceTemplatePath"], conf["grafanaServiceName"], conf["grafanaRootDir"], conf["grafanaTheme"], conf["customCssFile"])
    print ("Service registered and inital patching done.")
    print ("Remind to either restart the grafana service (sudo systemctl restart %s) or the whole machine." % conf["grafanaServiceName"])
elif args.undo:
    print ("Undoing the patching and remove the service...")
    if restoreGrafanaIndexFile(conf["grafanaIndexFilePath"], conf["backupExtension"]):
        removeGrafanaIndexBackupFiles(conf["grafanaIndexFilePath"], conf["backupExtension"])
        removeCustomCSSDir(conf["grafanaRootDir"], conf["customCSSDir"])
    
    removeSystemService(conf["patchServiceName"], os.path.join(conf["systemdPath"], conf["patchServiceName"]))
    print ("Finished removal.")
    print ("Remind to either restart the grafana service (sudo systemctl restart %s) or the whole machine." % conf["grafanaServiceName"])
else:
    print ("Patching the grafana index file if needed...")
    patchGrafanaIndexFile(conf["grafanaIndexFilePath"], conf["backupExtension"], conf["grafanaTheme"], conf["customCssFile"])
    print ("Patching done.")
