import subprocess
import json
from databaseSetup import setupDatabase, addPackageToDatabase
from npmCalls import getWeeklyDownloads, getMonthlyDownloads, getLastUpdate

def main():
    setupDatabase()

    result = subprocess.run(["node", "code/getTopPackages.js"], capture_output=True, text=True)
    topPackages = json.loads(result.stdout)

    for packageName in topPackages:
        weeklyDownloads = getWeeklyDownloads(packageName)
        monthlyDownloads = getMonthlyDownloads(packageName)
        lastUpdate = getLastUpdate(packageName)

        if weeklyDownloads and monthlyDownloads and lastUpdate:
            addPackageToDatabase(packageName, weeklyDownloads, monthlyDownloads, lastUpdate)
        else:
            print(f"Failed to retrieve data for package: {packageName}")

    print(f"Database population complete for {len(topPackages)} packages")


if __name__ == "__main__":
    main()