import requests
from datetime import datetime

def checkPackageExists(packageName : str):
    try:
        url = f"https://registry.npmjs.org/{packageName}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            date = data["time"]["modified"]
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            weeklyDownloads = getWeeklyDownloads(packageName)
            monthlyDownloads = getMonthlyDownloads(packageName)
            return weeklyDownloads, monthlyDownloads, dt.strftime("%d-%m-%Y %H:%M:%S")
        else:
            return False
    except Exception as e:
        print(f"CheckPackageExists: Error is {e}")
        return False
    
def checkBulkPackageExists(packageNames : list): # Output from the fucntion is a dictionary like {'react': True, 'wvrvnwuvow': False}
    try:
        results = {}
        batchString = ",".join(packageNames)
        url = f"https://api.npmjs.org/downloads/point/last-week/{batchString}"
        response = requests.get(url)
        data = response.json()
        for packageName in packageNames:
            pkg_data = data.get(packageName)
            results[packageName] = (pkg_data is not None and isinstance(pkg_data, dict))

        return results
    except Exception as e:
        print(f"checkBulkPackageExists: Error is {e}")
        return {}

def getWeeklyDownloads(packageName : str):
    try:
        url = f" https://api.npmjs.org/downloads/point/last-week/{packageName}"
        response = requests.get(url)
        data = response.json()
        return data.get("downloads")
    except Exception as e:
        print(f"getWeeklyDownloads: Error is {e}")
        return None
    
def getMonthlyDownloads(packageName : str):
    try:
        url = f" https://api.npmjs.org/downloads/point/last-month/{packageName}"
        response = requests.get(url)
        data = response.json()
        downloads = data.get("downloads")
        return downloads
    except Exception as e:
        print(f"getMonthlyDownloads: Error is {e}")
        return None

def getLastUpdate(packageName : str):
    try:
        url = f"https://registry.npmjs.org/{packageName}"
        response = requests.get(url)
        data = response.json()
        date = data["time"]["modified"]
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
        return dt.strftime("%d-%m-%Y %H:%M:%S")
    except Exception as e:
        print(f"getLastUpdate: Error is {e}")
        return None
    
def getBatchWeeklyDownloads(batchString: str):
    try:
        url = f"https://api.npmjs.org/downloads/point/last-week/{batchString}"
        response = requests.get(url)
        data = response.json()
        return {pkg: data[pkg] for pkg in data if pkg != "start" and pkg != "end"}
    except Exception as e:
        print(f"getBatchWeeklyDownloads: Error is {e}")
        return {}

def getBatchMonthlyDownloads(batchString: str):
    try:
        url = f"https://api.npmjs.org/downloads/point/last-month/{batchString}"
        response = requests.get(url)
        data = response.json()
        return {pkg: data[pkg] for pkg in data if pkg != "start" and pkg != "end"}
    except Exception as e:
        print(f"getBatchMonthlyDownloads: Error is {e}")
        return {}
    
def getBatchLastUpdate(packageNames: list):
    try:
        lastUpdates = {}
        for packageName in packageNames:
            url = f"https://registry.npmjs.org/{packageName}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                date = data["time"]["modified"]
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                lastUpdates[packageName] = dt.strftime("%d-%m-%Y %H:%M:%S")
            else:
                lastUpdates[packageName] = None
        return lastUpdates
    except Exception as e:
        print(f"getBatchLastUpdate: Error is {e}")
        return {}