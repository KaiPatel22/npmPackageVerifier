import subprocess
import json
from databaseSetup import setupDatabase, addPackageToDatabase
from npmCalls import checkPackageExists
import sqlite3

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

    for packageName in topPackages:
        if isPackageInLegimateDatabase(packageName) == False:
            if checkPackageExists(packageName) != False:
                weeklyDownloads, monthlyDownloads, lastUpdate = checkPackageExists(packageName)
                if weeklyDownloads and monthlyDownloads and lastUpdate:
                    addPackageToDatabase(packageName, weeklyDownloads, monthlyDownloads, lastUpdate)
                else:
                    print(f"Failed to retrieve data for package: {packageName}")
        else:
            print(f"Package {packageName} already exists in the legitimate database.")
            
    print(f"Database population complete for {len(topPackages)} packages")


if __name__ == "__main__":
    main()