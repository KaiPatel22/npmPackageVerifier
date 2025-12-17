#!/usr/bin/env python3
import sys
import subprocess
from datetime import datetime, timedelta
import platform 
from npmCalls import getWeeklyDownloads, getMonthlyDownloads, getLastUpdate
import sqlite3

def checkInTyposquattedDB(packageName: str) -> int:
    connect = sqlite3.connect('database/typosquatted.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM typosquatted WHERE packageName=?", (packageName,))
    result = cursor.fetchone()
    connect.close()

    if result:
        return result
    return None

def calculateIndexScoreForTyposquatting(originalPackage: str, weeklyDownloads: int, monthlyDownloads: int, lastUpdate: str, message : str) -> int:
    indexScore = 0
    connect = sqlite3.connect('database/legitimate.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM legitimate WHERE packageName=?", (originalPackage,))
    result = cursor.fetchone()
    originalWeeklyDownloads = result[2]
    originalMonthlyDownloads = result[3]
    originalLastUpdate = result[4]
    connect.close()
    msg = message.lower()

    if "homograph" in msg:
        indexScore += 5
    if "levenshtein" in msg:
        indexScore += 4
    if "combosquatting" in msg:
        indexScore += 3
    if "hyphen/underscore" in msg:
        indexScore += 2

    downloadDifferenceWeekly = abs(originalWeeklyDownloads - weeklyDownloads)
    downloadDifferenceMonthly = abs(originalMonthlyDownloads - monthlyDownloads)

    if downloadDifferenceWeekly / originalWeeklyDownloads >= 0.1 or downloadDifferenceMonthly / originalMonthlyDownloads >= 0.1:
        indexScore += 5
    elif downloadDifferenceWeekly / originalWeeklyDownloads >= 0.2 or downloadDifferenceMonthly / originalMonthlyDownloads >= 0.2:
        indexScore += 3
    if downloadDifferenceWeekly / originalWeeklyDownloads >= 0.5 or downloadDifferenceMonthly / originalMonthlyDownloads >= 0.5:
        indexScore += 1

    return indexScore

def main():
    if len(sys.argv) < 3 and (sys.argv[1] != "install" or sys.argv[1] != "update"):
        print("Usage: nscan install <package> || nscan update <package>")
        sys.exit(1)


    typeOfCommand = sys.argv[1]
    packageName = sys.argv[2]

    if not checkInTyposquattedDB(packageName):
        print(f"Package not in database, getting information for {packageName}...")
        weeklyDownloads = getWeeklyDownloads(packageName)
        monthlyDownloads = getMonthlyDownloads(packageName)
        lastUpdate = getLastUpdate(packageName)
    else:
        print(f"Fetching {packageName} information from typosquatted database...")
        packageInfo = checkInTyposquattedDB(packageName)
        originalPackage = packageInfo[2]
        weeklyDownloads = packageInfo[3]
        monthlyDownloads = packageInfo[4]
        lastUpdate = packageInfo[5]
        message = packageInfo[6]
        calculateIndexScoreForTyposquatting(originalPackage, weeklyDownloads, monthlyDownloads, lastUpdate, message)

    downloadLowerBound = (weeklyDownloads * 4) * 0.9
    downloadUpperBound = (weeklyDownloads * 4) * 1.1

    def isPackageOutdated(lastUpdate : str):
        lastUpdateDate = datetime.strptime(lastUpdate, "%d-%m-%Y %H:%M:%S")
        sixMonthsAgo = datetime.now() - timedelta(days=6 * 30)
        return lastUpdateDate < sixMonthsAgo

    if (monthlyDownloads < downloadLowerBound) or (monthlyDownloads > downloadUpperBound) or (weeklyDownloads < 100000) or (monthlyDownloads < 1000000):
        print("WARNING: Package download information is suspicious")
        redText(f"Weekly downloads for {packageName}: {weeklyDownloads}")
        redText(f"Monthly downloads for {packageName}: {monthlyDownloads}")
        indexScore = calculateIndexScoreForTyposquatting(originalPackage, weeklyDownloads, monthlyDownloads, lastUpdate, message)
        print(f"Index score for {packageName}: {indexScore}")
    else:
        greenText(f"Weekly downloads for {packageName}: {weeklyDownloads}")
        greenText(f"Monthly downloads for {packageName}: {monthlyDownloads}")
    if (isPackageOutdated(lastUpdate)):
        print("WARNING: Package last update information is suspicious")
        redText(f"Last update to {packageName} is: {lastUpdate}")
        indexScore = calculateIndexScoreForTyposquatting(originalPackage, weeklyDownloads, monthlyDownloads, lastUpdate, message)
        print(f"Index score for {packageName}: {indexScore}")
    else:
        greenText(f"Last update to {packageName} is: {lastUpdate}")


    if typeOfCommand == "install":
        continueInstallation = input("Are you sure you want to continue with the installation (y/n):").lower()
        while continueInstallation != "y" and continueInstallation != "n":
            continueInstallation = input("Are you sure you want to continue with the installation (y/n):").lower()

        if continueInstallation == "y":
            npm_command = "npm.cmd" if platform.system() == "Windows" else "npm"
            installation = subprocess.run([npm_command, "install", packageName])
            sys.exit(installation.returncode)
        elif continueInstallation == "n":
            print(f"Aborting installation of {packageName}")
            sys.exit()
    else:
        continueUpdate = input("Are you sure you want to continue with the update (y/n):").lower()
        while continueUpdate != "y" and continueUpdate != "n":
            continueUpdate = input("Are you sure you want to continue with the update (y/n):").lower()

        if continueUpdate == "y":
            npm_command = "npm.cmd" if platform.system() == "Windows" else "npm"
            update = subprocess.run([npm_command, typeOfCommand, packageName])
            sys.exit(update.returncode)
        elif continueUpdate == "n":
            print(f"Aborting update of {packageName}")
            sys.exit()

    
def redText(text):
    print(f"\033[31m{text}\033[0m")

def greenText(text):
    print(f"\033[32m{text}\033[0m")

if __name__ == "__main__":
    main()
