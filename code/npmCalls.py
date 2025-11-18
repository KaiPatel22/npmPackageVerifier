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
        print(f"Error is {e}")
        return False

def getWeeklyDownloads(packageName : str):
    try:
        url = f" https://api.npmjs.org/downloads/point/last-week/{packageName}"
        response = requests.get(url)
        data = response.json()
        return data.get("downloads")
    except Exception as e:
        print(f"Error is {e}")
        return None
    
def getMonthlyDownloads(packageName : str):
    try:
        url = f" https://api.npmjs.org/downloads/point/last-month/{packageName}"
        response = requests.get(url)
        data = response.json()
        downloads = data.get("downloads")
        return downloads
    except Exception as e:
        print(f"Error is: {e}")
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
        print(f"Error is {e}")
        return None