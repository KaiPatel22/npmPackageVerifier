import subprocess
import json
from databaseSetup import setupDatabase, addPackageToDatabase
from npmCalls import getBatchWeeklyDownloads, getBatchMonthlyDownloads, getBatchLastUpdate, getWeeklyDownloads, getMonthlyDownloads, getLastUpdate
import sqlite3
import time

'''
File used to populate the legitimate database with packages 
'''

def isPackageInLegimateDatabase(packageName: str) -> bool:
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM legitimate WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0

'''
Removes any heavily depended on packages with low download counts from the database
'''
def removeLowDownloads(minWeekly: int = 10000, minMonthly: int = 100000):
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM legitimate WHERE weeklyDownloads < ? OR monthlyDownloads < ?''', (minWeekly, minMonthly))
    connect.commit()
    connect.close()


'''
Batches and populates the legitimate database with the package information from the api calls
'''
def main():
    setupDatabase()

    result = subprocess.run(["node", "code/getTopPackages.js"], capture_output=True, text=True)
    topPackages = json.loads(result.stdout)
    packagesToAdd = [pkg for pkg in topPackages if not isPackageInLegimateDatabase(pkg)]
    nonScopedPackages = [pkg for pkg in packagesToAdd if not pkg.startswith('@')]
    scopedPackages = [pkg for pkg in packagesToAdd if pkg.startswith('@')]

    maxPackageSize = 128

    for i in range(0, len(nonScopedPackages), maxPackageSize):
        batch = nonScopedPackages[i: i + maxPackageSize]
        batchString = ",".join(batch)
        print("-----------------------------------------")
        print(f"Processing {i} to {i + len(batch)} out of {len(nonScopedPackages)} packages")
        print("-----------------------------------------")
        weeklyData = getBatchWeeklyDownloads(batchString)
        monthlyData = getBatchMonthlyDownloads(batchString)
        lastUpdateData = getBatchLastUpdate(batch)

        for packageName in batch:
            weeklyDownloads = weeklyData.get(packageName, {}).get("downloads") if packageName in weeklyData else None
            monthlyDownloads = monthlyData.get(packageName, {}).get("downloads") if packageName in monthlyData else None
            lastUpdate = lastUpdateData.get(packageName)
            
            if weeklyDownloads and monthlyDownloads and lastUpdate and weeklyDownloads <= 10000 and monthlyDownloads <= 100000:
                addPackageToDatabase(packageName, weeklyDownloads, monthlyDownloads, lastUpdate)
                print(f"Added package: {packageName}")
            else:
                print(f"Failed to retrieve data for package: {packageName}")
    removeLowDownloads() # fallback pruning case for low downloads

    # print(f"Processing {len(scopedPackages)} scoped packages") SCOPED PACKAGES CAUSE RATE LIMITING ISSUES, CANT CHAIN THEM IN URL
    # for scopedPackageName in scopedPackages:
    #     print(f"Testing scoped package: {scopedPackageName}")
    #     weeklyDownload = getWeeklyDownloads(scopedPackageName)
    #     monthlyDownload = getMonthlyDownloads(scopedPackageName)
    #     lastUpdate = getLastUpdate(scopedPackageName)

    #     if weeklyDownload and monthlyDownload and lastUpdate:
    #         addPackageToDatabase(scopedPackageName, weeklyDownload, monthlyDownload, lastUpdate)
    #         print(f"Added scoped package: {scopedPackageName}")
    #     else:
    #         print(f"Failed to retrieve data for scoped package: {scopedPackageName}")

    # print(f"Database population complete for {len(nonScopedPackages)} packages")



if __name__ == "__main__":
    main()