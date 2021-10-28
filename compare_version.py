#!/usr/bin/env python3
import json
import sys
import requests
import urllib
import csv
from tomorrow import threads
__DOMAIN_NAME__ = 'http://localhost:8080'
__APTLY_REPO_NAME__ = "test-main-repo"
__APTLY_API_URL__ = "{}/api".format(__DOMAIN_NAME__)
result_csv_file = "result.csv"


def searchQuery(strQuery):
    return urllib.parse.quote(strQuery)


def getSourcePackageVersion(package_name):
    '''
    Only return Source Package Name And Version
    '''
    r = requests.get("{}/repos/{}/packages?q={}"
                     .format(__APTLY_API_URL__,
                             __APTLY_REPO_NAME__,
                             searchQuery(
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
                             searchQuery(
                                 "!$PackageType (= source), Source (= {})"
                                 .format(package_name))
                             )
                     ).text
    binaryPackages = json.loads(r)
    binaryPackagesList = []
    for i in range(len(binaryPackages)):
        # binaryPackages[i]: Parm64 qemu-system-common 1:3.1+dfsg-8~deb10u1 a0cc268b9a9a880f
        version = binaryPackages[i].split(' ')[2]
        name = binaryPackages[i].split(' ')[1]
        arch = binaryPackages[i].split(' ')[0]
        data = {
            "binaryArch": arch,
            "binaryName": name,
            "binaryVersion": version
        }
        binaryPackagesList.append(data)
    return binaryPackagesList


@threads(1000)
def compareSourceBinaryVersion(package_name):
    '''
    Compare Source And Binary version different
    '''
    sourcePackagesList = getSourcePackageVersion(package_name)
    binaryPackagesList = getBinaryPackageVersion(package_name)
    diffList = []
    for sourcePackage in sourcePackagesList:
        for binaryPackage in binaryPackagesList:
            # When version is different, append to diffList
            if (binaryPackage["binaryVersion"] != sourcePackage["sourceVersion"]):
                data = {"sourceName":  sourcePackage["sourceName"],
                        "sourceVersion": sourcePackage["sourceVersion"],
                        "binaryArch": binaryPackage["binaryArch"],
                        "binaryName": binaryPackage["binaryName"],
                        "binaryVersion": binaryPackage["binaryVersion"]}
                f = open(result_csv_file, "a+")
                writer = csv.writer(f)
                writer.writerow(
                    [sourcePackage["sourceName"],
                     sourcePackage["sourceVersion"],
                     binaryPackage["binaryArch"],
                     binaryPackage["binaryName"],
                     binaryPackage["binaryVersion"]
                     ])
                f.close()

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
                             searchQuery(
                                 "$PackageType (= source)"))
                     ).text
    sourcePackagesList = []
    for i in json.loads(r):
        sourcePackagesList.append(i.split(' ')[1])
    sourcePackagesList.sort()
    return sourcePackagesList


def main():
    sourcePackagesLists = getSourcePackagesList()

    with open(result_csv_file, "w") as result_csv:
        writer = csv.writer(result_csv)
        writer.writerow(["sourceName", "sourceVersion",
                        "binaryArch", "binaryName", "binaryVersion"])
    result_csv.close()
    for sourcePackage in sourcePackagesLists:
        compareSourceBinaryVersion(sourcePackage)


if __name__ == "__main__":
    main()
