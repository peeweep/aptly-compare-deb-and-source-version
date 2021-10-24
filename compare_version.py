#!/usr/bin/env python3
import json
import sys
import requests
import urllib
__DOMAIN_NAME__ = 'http://localhost:8080'
__APTLY_REPO_NAME__ = "test-main-repo"
__APTLY_API_URL__ = "{}/api".format(__DOMAIN_NAME__)


def getSourcePackageVersion(package_name):
    '''
    Only return Source Package Name And Version
    '''
    r = requests.get("{}/repos/{}/packages?q={}"
                     .format(__APTLY_API_URL__,
                             __APTLY_REPO_NAME__,
                             urllib.parse.quote(
                                 "$PackageType (= source), Name (= {})"
                                 .format(package_name))
                             )
                     ).text
    sourcePackages = json.loads(r)
    sourcePackagesList = []
    for i in range(len(sourcePackages)):
        version = sourcePackages[i].split(' ')[2]
        data = {
            "sourceName": package_name,
            "sourceVersion": version
        }
        sourcePackagesList.append(data)
    return sourcePackagesList


def getBinaryPackageVersion(package_name):
    '''
    Only return non-Source Package
    '''
    r = requests.get("{}/repos/{}/packages?q={}"
                     .format(__APTLY_API_URL__,
                             __APTLY_REPO_NAME__,
                             urllib.parse.quote(
                                 "!$PackageType (= source), Source (= {})"
                                 .format(package_name))
                             )
                     ).text
    binaryPackages = json.loads(r)
    binaryPackagesList = []
    for i in range(len(binaryPackages)):
        version = binaryPackages[i].split(' ')[2]
        name = binaryPackages[i].split(' ')[1]
        data = {
            "binaryName": name,
            "binaryVersion": version
        }
        binaryPackagesList.append(data)
    return binaryPackagesList


def compareSourceBinaryVersion(sourcePackagesList, binaryPackagesList):
    '''
    Compare Source And Binary version different
    '''
    diffList = []
    for sourcePackage in sourcePackagesList:
        for binaryPackage in binaryPackagesList:
            # When version is different, append to diffList
            if (binaryPackage["binaryVersion"] !=
                    sourcePackage["sourceVersion"]):
                data = {"sourceName":  sourcePackage["sourceName"],
                        "sourceVersion": sourcePackage["sourceVersion"],
                        "binaryName": binaryPackage["binaryName"],
                        "binaryVersion": binaryPackage["binaryVersion"]}
                diffList.append(data)
    for diff in diffList:
        print(diff)


def getSourcePackagesList():
    '''
    List all source packages
    '''
    r = requests.get("{}/repos/{}/packages?q={}"
                     .format(__APTLY_API_URL__,
                             __APTLY_REPO_NAME__,
                             urllib.parse.quote(
                                 "$PackageType (= source)"))
                     ).text
    sourcePackagesList = []
    for i in json.loads(r):
        sourcePackagesList.append(i.split(' ')[1])
    return sourcePackagesList


def main():
    sourcePackagesList = getSourcePackagesList()
    for sourcePackage in sourcePackagesList:
        sourcePackagesList = getSourcePackageVersion(
            package_name=sourcePackage)
        binaryPackagesList = getBinaryPackageVersion(
            package_name=sourcePackage)
        compareSourceBinaryVersion(sourcePackagesList, binaryPackagesList)


if __name__ == "__main__":
    main()
