import requests
from datetime import datetime
import time

# def sleepTime(response, defaultSleep = 10.0):
#     try:
#         retryTime = response.headers.get("Retry-After")
#         timeVal = float(retryTime) if retryTime is not None else 0.0
#         if timeVal <= 0:
#             timeVal = float(defaultSleep)
#             print(f"SLEEPING for {timeVal} due to rate limiting")
#             time.sleep(float(timeVal)) 
#         else:
#             time.sleep(float(timeVal))
#             print(f"SLEEPING for {timeVal} seconds due to rate limiting")
#     except Exception as e:
#         time.sleep(float(defaultSleep))
#         print(f"sleepTime: Error is {e}, sleeping for default {defaultSleep} seconds")

def dataProccess(url: str, retries: int = 3, delay: float = 15.0):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"SLEEPING due to rate limiting for URL: {url}")
                time.sleep(10.0)
            else:
                print(f"retryProcess: Received status code {response.status_code} for URL: {url}")
        except Exception as e:
            print(f"retryProcess: Error is {e} on attempt {attempt + 1} for URL: {url}")
        attempt += 1
        time.sleep(delay)
    return None

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

        if response.status_code != 200:
            if response.status_code == 429:
                print(f"SLEEPING due to rate limiting for URL: {url}")
                time.sleep(10.0)
            return {}
    
        data = response.json()

        for packageName in packageNames:
            pkg_data = data.get(packageName)
            results[packageName] = (isinstance(pkg_data, dict) and "downloads" in pkg_data and isinstance(pkg_data.get("downloads"), int))

        return results
    except Exception as e:
        print(f"checkBulkPackageExists: Error is {e}")
        return {}

def getWeeklyDownloads(packageName : str):
    try:
        url = f"https://api.npmjs.org/downloads/point/last-week/{packageName}"
        response = requests.get(url)

        data = dataProccess(url)
        return data.get("downloads")
    except Exception as e:
        print(f"getWeeklyDownloads: Error is {e}")
        return None
    
def getMonthlyDownloads(packageName : str):
    try:
        url = f"https://api.npmjs.org/downloads/point/last-month/{packageName}"
        response = requests.get(url)
        data = dataProccess(url)
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

        if response.status_code != 200:
            if response.status_code == 429:
                print(f"SLEEPING due to rate limiting for URL: {url}")
                time.sleep(10.0)
            return {}

        data = response.json()
        out = {}
        for pkg, payload in data.items():
            if pkg in ("start", "end"):
                continue
            if isinstance(payload, dict) and isinstance(payload.get("downloads"), int):
                out[pkg] = payload
        return out
    except Exception as e:
        print(f"getBatchWeeklyDownloads: Error is {e}")
        return {}

def getBatchMonthlyDownloads(batchString: str):
    try:
        url = f"https://api.npmjs.org/downloads/point/last-month/{batchString}"
        response = requests.get(url)

        if response.status_code != 200:
            if response.status_code == 429:
                print(f"SLEEPING due to rate limiting for URL: {url}")
                time.sleep(10.0)
            return {}

        data = response.json()
        out = {}
        for pkg, payload in data.items():
            if pkg in ("start", "end"):
                continue
            if isinstance(payload, dict) and isinstance(payload.get("downloads"), int):
                out[pkg] = payload
        return out
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