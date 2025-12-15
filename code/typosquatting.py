import Levenshtein
import sqlite3
from npmCalls import checkPackageExists, checkBulkPackageExists, getBatchWeeklyDownloads, getBatchMonthlyDownloads, getBatchLastUpdate
import time 

def createTyposquattingDatabase():
    connect = sqlite3.connect("database/typosquatted.db")
    cursor = connect.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS typosquatted(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                packageName TEXT UNIQUE NOT NULL,
                typosquattedFrom TEXT NOT NULL,
                weeklyDownloads INTEGER NOT NULL,
                monthlyDownloads INTEGER NOT NULL,
                lastUpdate TIMESTAMP NOT NULL, 
                detectionMethods TEXT NOT NULL)
                ''')
    connect.commit()
    connect.close()
    print("Typosquatting database setup complete.")

def createNotCreatedDatabase():
    connect = sqlite3.connect("database/notCreated.db")
    cursor = connect.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notCreated(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                packageName TEXT UNIQUE NOT NULL)
                ''')
    connect.commit()
    connect.close()
    print("NotCreated database setup complete.")


def packageNamesFromDatabase():
    createTyposquattingDatabase()
    createNotCreatedDatabase()
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT packageName FROM legitimate''')
    rows = cursor.fetchall()
    packageNames = [row[0] for row in rows]

    possibleTyposquatting = []
    
    for package in packageNames:
        possibleTyposquatting.extend(levenshteinCheck(package))
        possibleTyposquatting.extend(homographCheck(package))
        possibleTyposquatting.extend(combosquattingCheck(package))
        possibleTyposquatting.extend(hyphenUnderscoreCheck(package))

    processBatches(possibleTyposquatting)

    connect.close()
    return packageNames

def addPackageToTyposqauttedDatabase(packageName: str, typoSquattedFrom : str, weeklyDownloads: int, monthlyDownloads: int, lastUpdate: str, detectionMethods: str):
    connect = sqlite3.connect("database/typosquatted.db")
    cursor = connect.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO typosquatted (packageName, typosquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods)
        VALUES (?, ?, ?, ?, ?, ?)''', (packageName, typoSquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods))
    connect.commit()
    connect.close()

def addPackageToNotCreatedDatabase(packageName: str):
    connect = sqlite3.connect("database/notCreated.db")
    cursor = connect.cursor()
    cursor.execute('''INSERT OR IGNORE INTO notCreated (packageName) VALUES (?)''', (packageName,))
    connect.commit()
    connect.close()

def isPackageInTyposquattedDatabase(packageName: str) -> bool:
    connect = sqlite3.connect("database/typosquatted.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM typosquatted WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0

def isPackageInNotCreatedDatabase(packageName: str) -> bool:
    connect = sqlite3.connect("database/notCreated.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM notCreated WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0

def processBatches(generatedList : list):
    batchSize = 128
    filteredPackages = [package for package in generatedList if not isPackageInTyposquattedDatabase(package[0]) and not isPackageInNotCreatedDatabase(package[0])]

    print(f"Total packages to check: {len(filteredPackages)}")
    print(f"Total Batches: {(len(filteredPackages) + batchSize - 1) // batchSize}")

    for i in range(0, len(filteredPackages), batchSize):
        batch = filteredPackages[i:i+batchSize]
        typosquattedNames = [item[0] for item in batch]
        results = checkBulkPackageExists(typosquattedNames)

        existingPackages = [name for name in typosquattedNames if results.get(name)]

        weeklyData = {}
        monthlyData = {}
        lastUpdateData = {}
        typosquattedCount = 0
        notCreatedCount = 0

        if existingPackages:
            batchString = ",".join(existingPackages)
            weeklyData = getBatchWeeklyDownloads(batchString)
            monthlyData = getBatchMonthlyDownloads(batchString)
            lastUpdateData = getBatchLastUpdate(existingPackages)

        for modifiedName, originalName, message in batch:
            if results.get(modifiedName, False):
                weeklyDownloads = weeklyData.get(modifiedName, {}).get("downloads") if modifiedName in weeklyData else None
                monthlyDownloads = monthlyData.get(modifiedName, {}).get("downloads") if modifiedName in monthlyData else None
                lastUpdate = lastUpdateData.get(modifiedName)
                addPackageToTyposqauttedDatabase(modifiedName, originalName, weeklyDownloads, monthlyDownloads, lastUpdate, message)
                typosquattedCount += 1
                redText(f"Added {modifiedName} to typosquatted database, detected via {message}")
            else:
                addPackageToNotCreatedDatabase(modifiedName)
                notCreatedCount += 1
        print("-----------------------------------------")
        greenText(f"Not created added: {notCreatedCount}")
        redText(f"Typosquatted added: {typosquattedCount}")
        print("-----------------------------------------")

        time.sleep(0.5)

def placeholder(modifiedName : str, packageName : str, message : str):
    if not isPackageInTyposquattedDatabase(modifiedName) and not isPackageInNotCreatedDatabase(modifiedName):
        print(f"Checking {modifiedName}...")
        call = checkPackageExists(modifiedName)
        if call is not False:
            weeklyDownloads, monthlyDownloads, lastUpdate = call
            addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, message)
            redText(f"Added {modifiedName} to typosquatted database, detected via {message}")
        else:
            addPackageToNotCreatedDatabase(modifiedName)
    else:
        greenText(f"{modifiedName} already in a database, skipping check.")

# Check 1: Levenstein distance 
def levenshteinCheck(packageName: str):
    generated = []
    generated.append((packageName + "s", packageName, "Levenshtein distance - added 's'"))
    generated.append((packageName + packageName[-1], packageName, "Levenshtein distance - duplicated last character"))

    for i in range(len(packageName)):
        modifiedName = packageName[:i] + packageName[i+1:]
        generated.append((modifiedName, packageName, f"Levenshtein distance - removed character at position {i}"))
    
    for i in range(len(packageName) - 1):
        if packageName[i] == packageName[i+1]:
            continue
        modifiedName = packageName[:i] + packageName[i+1] + packageName[i] + packageName[i+2:]
        generated.append((modifiedName, packageName, f"Levenshtein distance - swapped characters at positions {i} and {i+1}"))

    return generated

# Check 2: Homograph attacks
def homographCheck(packageName : str):
    generated = []
    HOMOGRAPH_MAP = {
        "a": ["а \u0430", "ɑ \u0251", "à \u00E0", "á \u00E1", "â \u00E2", "ä \u00E4", "ã \u00E3"],
        "b": ["Ь \u042C", "Ƅ \u0184", "ƅ \u0185", "Ь \u044C"],

        "c": ["ϲ \u03F2", "с \u0441", "ƈ \u0188"],
        "d": ["ԁ \u0501", "ɗ \u0257"],

        "e": ["е \u0435", "є \u0454", "℮ \u212E", "é \u00E9", "ê \u00EA", "ë \u00EB"],
        "f": ["ғ \u0493", "ƒ \u0192"],

        "g": ["ɡ \u0261", "ġ \u0121", "ğ \u011F"],
        "h": ["һ \u04BB", "հ \u0570"],

        "i": ["ӏ \u04CF", "ı \u0131", "İ \u0130", "¡ \u00A1", "l \u006C", "1 \u0031"],
        "j": ["ј \u0458"],
        "k": ["κ \u03BA", "к \u043A"],
        "l": ["Ɩ \u0196", "ӏ \u04CF", "ⅼ \u217C", "Ι \u0399"],

        "m": ["м \u043C"],
        "n": ["ո \u0576", "п \u043F"],

        "o": ["ο \u03BF", "о \u043E", "ɵ \u0275", "ö \u00F6", "ò \u00F2", "ó \u00F3"],
        "p": ["р \u0440", "ρ \u03C1"],

        "q": ["զ \u0566"],
        "r": ["г \u0433", "ṛ \u1E5B"],
        "s": ["ѕ \u0455", "ʂ \u0282"],
        "t": ["τ \u03C4", "т \u0442"],

        "u": ["υ \u03C5", "ü \u00FC", "û \u00FB", "ú \u00FA"],
        "v": ["ν \u03BD", "ѵ \u0475"],
        "w": ["ш \u0448", "ԝ \u051D"],
        "x": ["х \u0445", "χ \u03C7"],
        "y": ["у \u0443", "ү \u04AF"],
        "z": ["ʐ \u0290", "ž \u017E"],

        # DIGITS
        "0": ["O \u004F", "О \u041E", "ο \u03BF", "○ \u25CB"],
        "1": ["l \u006C", "I \u0049", "ӏ \u04CF"],
        "2": ["Ƨ \u01A7"],
        "3": ["З \u0417", "ɜ \u025C"],
        "4": ["Ꮞ \u13CE"],
        "5": ["Ƽ \u01BC"],
        "6": ["б \u0431"],
        "7": ["Τ \u03A4"],
        "8": ["੪ \u0A6A"],
        "9": ["९ \u096F"],

        # PUNCTUATION / SPECIAL
        "-": ["‐ \u2010", "- \u2011", "– \u2013", "— \u2014", "− \u2212"],
        ".": ["․ \u2024", "• \u2022", "。 \u3002"],
        "_": ["﹍ \uFE4D", "＿ \uFF3F"],
        "/": ["∕ \u2215"],
        "\\": ["＼ \uFF3C"],
    }

    for letter in packageName:
        if letter in HOMOGRAPH_MAP:
            for homograph in HOMOGRAPH_MAP[letter]:
                homograph_stripped = homograph.split(" ")[1] # gets the actual homographic character
                modifiedName = packageName.replace(letter,homograph_stripped)
                generated.append((modifiedName, packageName, f"Homograph attack - replaced {letter} with {homograph_stripped}"))
    return generated


# Check 3: Combosquatting attacks
def combosquattingCheck(packageName : str):
    generated = []
    prefixes = [
    "node-", "js-", "ts-", "ng-", "react-", "vue-", "next-", "express-", "cli-", "utils-", "lib-",
    "crypto-", "secure-", "safe-", "auth-", "jwt-", "npmjs-", "github-"
    ]

    suffixes = [
    "-js", "-node", "-utils", "-helper", "-core", "-service", "-api", "-server", "-cli", "-module",
    "-v2", "-v3", "-beta", "-dev", "-next", "-lite", "-min", "-pro", "-plus",
    "-pkg", "-package", "-script", "-lib"
    ]

    for prefix in prefixes:
        generated.append((prefix + packageName, packageName, f"Combosquatting - added prefix {prefix}"))

   
    for suffix in suffixes:
        generated.append((packageName + suffix, packageName, f"Combosquatting - added suffix {suffix}"))
    
    return generated

# Check 4: Hyphen/underscore manipulation 
def hyphenUnderscoreCheck(packageName : str):
    generated = []
    if "-" in packageName:
        generated.append((packageName.replace("-", "_"), packageName, f"Hyphen/underscore manipulation"))
    elif "_" in packageName:
        generated.append((packageName.replace("_", "-"), packageName, f"Hyphen/underscore manipulation"))
    return generated

def redText(text):
    print(f"\033[31m{text}\033[0m")

def greenText(text):
    print(f"\033[32m{text}\033[0m")

if __name__ == "__main__":
    packageNamesFromDatabase()