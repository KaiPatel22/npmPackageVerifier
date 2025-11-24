import subprocess
import json
from databaseSetup import setupDatabase, addPackageToDatabase
from npmCalls import getBatchWeeklyDownloads, getBatchMonthlyDownloads, getBatchLastUpdate
import sqlite3
import time

def isPackageInLegimateDatabase(packageName: str) -> bool:
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM legitimate WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0


def main():
    setupDatabase()

    result = subprocess.run(["node", "code/getTopPackages.js"], capture_output=True, text=True)
    topPackages = json.loads(result.stdout)
    packagesToAdd = [pkg for pkg in topPackages if not isPackageInLegimateDatabase(pkg)]
    nonScopedPackages = [pkg for pkg in packagesToAdd if not pkg.startswith('@')]
    batchString = ",".join(nonScopedPackages)

    weeklyData = getBatchWeeklyDownloads(batchString)
    monthlyData = getBatchMonthlyDownloads(batchString)
    lastUpdateData = getBatchLastUpdate(nonScopedPackages)

    print(f"weeklyData: {weeklyData}")

    for packageName in packagesToAdd:
        weeklyDownloads = weeklyData.get(packageName, {}).get("downloads") if packageName in weeklyData else None
        monthlyDownloads = monthlyData.get(packageName, {}).get("downloads") if packageName in monthlyData else None
        lastUpdate = lastUpdateData.get(packageName)
        
        if weeklyDownloads and monthlyDownloads and lastUpdate:
            addPackageToDatabase(packageName, weeklyDownloads, monthlyDownloads, lastUpdate)
            print(f"Added package: {packageName}")
        else:
            print(f"Failed to retrieve data for package: {packageName}")

    print(f"Database population complete for {len(packagesToAdd)} packages")



if __name__ == "__main__":
    main()