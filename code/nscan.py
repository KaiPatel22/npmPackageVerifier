#!/usr/bin/env python3
import sys
import subprocess
from datetime import datetime, timedelta
import platform 
from npmCalls import getWeeklyDownloads, getMonthlyDownloads, getLastUpdate, getWeeklyDownloadsBasic, getMonthlyDownloadsBasic
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

def checkInLegitimateDB(packageName: str) -> int:
    connect = sqlite3.connect('database/legitimate.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM legitimate WHERE packageName=?", (packageName,))
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
        print("+5 index score for homograph attack")
        indexScore += 5
    if "levenshtein" in msg:
        print("+4 index score for levenshtein distance")
        indexScore += 4
    if "combosquatting" in msg:
        print("+3 index score for combosquatting")
        indexScore += 3
    if "hyphen/underscore" in msg:
        print("+2 index score for hyphen/underscore substitution")
        indexScore += 2

    downloadDifferenceWeekly = abs(originalWeeklyDownloads - weeklyDownloads)
    downloadDifferenceMonthly = abs(originalMonthlyDownloads - monthlyDownloads)

    print(f"Original weekly downloads: {originalWeeklyDownloads}, Typosquatted weekly downloads: {weeklyDownloads}, difference of {downloadDifferenceWeekly}")
    print(f"Original monthly downloads: {originalMonthlyDownloads}, Typosquatted monthly downloads: {monthlyDownloads}, difference of {downloadDifferenceMonthly}")

    if weeklyDownloads < 1000000 and monthlyDownloads < 10000000:
        if (downloadDifferenceWeekly / originalWeeklyDownloads >= 0.1) or (downloadDifferenceMonthly / originalMonthlyDownloads >= 0.1):
            print("+5 index score for significant download difference")
            indexScore += 5
        elif (downloadDifferenceWeekly / originalWeeklyDownloads >= 0.2) or (downloadDifferenceMonthly / originalMonthlyDownloads >= 0.2) and (weeklyDownloads < 1000000 and monthlyDownloads < 10000000):
            print("+3 index score for moderate download difference")
            indexScore += 3
        elif (downloadDifferenceWeekly / originalWeeklyDownloads >= 0.5) or (downloadDifferenceMonthly / originalMonthlyDownloads >= 0.5) and (weeklyDownloads < 1000000 and monthlyDownloads < 10000000):
            print("+1 index score for minor download difference")
            indexScore += 1
    else:
        print("No index score added for download difference due to high weekly and monthly download counts")

    return indexScore


def calculateSuspiciousIndexScore(weeklyDownloads: int, monthlyDownloads: int, lastUpdate: str) -> int:
    indexScore = 0 

    downloadLowerBound1 = (weeklyDownloads * 4) * 0.7
    downloadUpperBound1 = (weeklyDownloads * 4) * 1.3

    downloadLowerBound2 = (weeklyDownloads * 4) * 0.5
    downloadUpperBound2 = (weeklyDownloads * 4) * 1.5

    downloadLowerBound3 = (weeklyDownloads * 4) * 0.3
    downloadUpperBound3 = (weeklyDownloads * 4) * 1.7

    if (monthlyDownloads < downloadLowerBound1) or (monthlyDownloads > downloadUpperBound1):
        indexScore += 2
    elif (monthlyDownloads < downloadLowerBound2) or (monthlyDownloads > downloadUpperBound2):
        indexScore += 3
    elif (monthlyDownloads < downloadLowerBound3) or (monthlyDownloads > downloadUpperBound3):
        indexScore += 5

    def isPackageOutdated6months(lastUpdate : str):
        lastUpdateDate = datetime.strptime(lastUpdate, "%d-%m-%Y %H:%M:%S")
        sixMonthsAgo = datetime.now() - timedelta(days=6 * 30)
        return lastUpdateDate < sixMonthsAgo
    
    def isPackageOutdated1year(lastUpdate : str):
        lastUpdateDate = datetime.strptime(lastUpdate, "%d-%m-%Y %H:%M:%S")
        oneYearAgo = datetime.now() - timedelta(days=12 * 30)
        return lastUpdateDate < oneYearAgo
    
    def isPackageOutdated2years(lastUpdate : str):
        lastUpdateDate = datetime.strptime(lastUpdate, "%d-%m-%Y %H:%M:%S")
        twoYearsAgo = datetime.now() - timedelta(days=24 * 30)
        return lastUpdateDate < twoYearsAgo
    
    if (isPackageOutdated2years(lastUpdate)):
        indexScore += 4
    elif (isPackageOutdated1year(lastUpdate)):
        indexScore += 3
    elif (isPackageOutdated6months(lastUpdate)):
        indexScore += 2

    return indexScore


def main():
    if len(sys.argv) < 3 and (sys.argv[1] != "install" or sys.argv[1] != "update"):
        print("Usage: nscan install <package> || nscan update <package>")
        sys.exit(1)

    typeOfCommand = sys.argv[1]
    packageName = sys.argv[2]

    overallIndexScore = 0

    if not checkInTyposquattedDB(packageName) and not checkInLegitimateDB(packageName):
        print(f"Package not in database, getting information for {packageName}...")
        weeklyDownloads = getWeeklyDownloadsBasic(packageName)
        monthlyDownloads = getMonthlyDownloadsBasic(packageName)
        if weeklyDownloads is None or monthlyDownloads is None:
            yellowText(f"{packageName} does not exist. Exiting...")
            sys.exit(1)
        lastUpdate = getLastUpdate(packageName)
        suspiciousIndexScore = calculateSuspiciousIndexScore(weeklyDownloads, monthlyDownloads, lastUpdate)
        redText(f"Suspicious index score for {packageName}: {suspiciousIndexScore}")
        overallIndexScore += suspiciousIndexScore
    elif checkInTyposquattedDB(packageName):
        print(f"Fetching {packageName} information from typosquatted database...")
        packageInfo = checkInTyposquattedDB(packageName)
        originalPackage = packageInfo[2]
        weeklyDownloads = packageInfo[3]
        monthlyDownloads = packageInfo[4]
        lastUpdate = packageInfo[5]
        message = packageInfo[6]
        typosquattingIndexScore = calculateIndexScoreForTyposquatting(originalPackage, weeklyDownloads, monthlyDownloads, lastUpdate, message)
        redText(f"Typoquatting index score for {packageName}: {typosquattingIndexScore}")
        overallIndexScore += typosquattingIndexScore
    elif checkInLegitimateDB(packageName):
        print(f"Fetching {packageName} information from legitimate database...")
        packageInfo = checkInLegitimateDB(packageName)
        weeklyDownloads = packageInfo[2]
        monthlyDownloads = packageInfo[3]
        lastUpdate = packageInfo[4]
        greenText(f"{packageName} found in legitimate database, no index score added.")

    print(f"--------------------------------------------")
    print(f"Package Summary for {packageName}")
    print(f"Weekly Downloads: {weeklyDownloads}")
    print(f"Monthly Downloads: {monthlyDownloads}")
    print(f"Last Update: {lastUpdate}")
    if overallIndexScore >= 7:
        redText(f"Overall Index Score: {overallIndexScore}")
    elif overallIndexScore >=4 and overallIndexScore < 7:
        yellowText(f"Overall Index Score: {overallIndexScore}")
    else:
        greenText(f"Overall Index Score: {overallIndexScore}")
    print(f"--------------------------------------------")

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

def yellowText(text: str):
    print(f"\033[93m{text}\033[0m")

if __name__ == "__main__":
    main()
