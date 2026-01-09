import Levenshtein
import sqlite3
from npmCalls import checkPackageExists, checkBulkPackageExists, getBatchWeeklyDownloads, getBatchMonthlyDownloads, getBatchLastUpdate, getWeeklyDownloads, getMonthlyDownloads
import time 

'''
File used to generate possible typosquatted package name variations and checks if they exist before adding them to a database
'''

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

'''
After generating a full list of possible typosquatetd names, they are filtered down and then batched into 128 package chunks to be processed faster and less likely to hit rate limits
'''
def processBatches(generatedList : list):
    batchSize = 128
    filteredPackages = [package for package in generatedList if not isPackageInTyposquattedDatabase(package[0]) and not isPackageInNotCreatedDatabase(package[0])]
    totalPackages = len(filteredPackages)
    totalBatches = (totalPackages + batchSize - 1) // batchSize
    print(f"Total packages to check: {totalPackages}")
    print(f"Total Batches: {totalBatches}")

    reservedNames = {"start", "end", "package", "downloads"}

    for i in range(0, totalPackages, batchSize):
        batchNumber = (i // batchSize) + 1
        batch = filteredPackages[i:i+batchSize]
        typosquattedNames = [item[0] for item in batch]
        results = checkBulkPackageExists(typosquattedNames)

        if results == {}:
            print("Status code not 200, skipping...")
            continue

        existingPackages = [name for name in typosquattedNames if results.get(name)]

        weeklyData = {}
        monthlyData = {}
        lastUpdateData = {}
        typosquattedCount = 0
        notCreatedCount = 0

        if existingPackages:
            batchable = [name for name in existingPackages if name not in reservedNames]
            batchString = ",".join(batchable)
            weeklyData = getBatchWeeklyDownloads(batchString)
            monthlyData = getBatchMonthlyDownloads(batchString)
        
            for reserved in existingPackages:
                if reserved in reservedNames:
                    reservedWeeklyDownloads = getWeeklyDownloads(reserved)
                    reservedMonthlyDownloads = getMonthlyDownloads(reserved)
                    if isinstance(reservedWeeklyDownloads, int) and isinstance(reservedMonthlyDownloads, int):
                        weeklyData[reserved] = {"downloads": reservedWeeklyDownloads}
                        monthlyData[reserved] = {"downloads": reservedMonthlyDownloads}
            
            lastUpdateData = getBatchLastUpdate(existingPackages)

        for modifiedName, originalName, message in batch:
            if results.get(modifiedName, False):
                weeklyPayload = weeklyData.get(modifiedName)
                monthlyPayload = monthlyData.get(modifiedName)
                weeklyDownloads = weeklyPayload.get("downloads") if isinstance(weeklyPayload, dict) else None
                monthlyDownloads = monthlyPayload.get("downloads") if isinstance(monthlyPayload, dict) else None
                lastUpdate = lastUpdateData.get(modifiedName)

                # if weeklyDownloads is None: # Specific hardcoding if the download data is missing - Hashed this out due to bringing up rate liiting issues too quickly
                #     print(f"Weekly downloads missing for {modifiedName}, fetching specifically...")
                #     specificWeeklyDownloads = getWeeklyDownloads(modifiedName)
                #     if isinstance(specificWeeklyDownloads, int):
                #         weeklyDownloads = specificWeeklyDownloads
                # if monthlyDownloads is None:
                #     print(f"Monthly downloads missing for {modifiedName}, fetching specifically...")
                #     specificMonthlyDownloads = getMonthlyDownloads(modifiedName)
                #     if isinstance(specificMonthlyDownloads, int):
                #         monthlyDownloads = specificMonthlyDownloads

                if weeklyDownloads is None or monthlyDownloads is None or lastUpdate is None:
                    yellowText(f"Package missing is {modifiedName}")
                    yellowText(f"Weekly payload: {weeklyPayload}, Monthly payload: {monthlyPayload}, Last update data: {lastUpdateData}")
                    continue
                addPackageToTyposqauttedDatabase(modifiedName, originalName, weeklyDownloads, monthlyDownloads, lastUpdate, message)
                typosquattedCount += 1
                redText(f"Added {modifiedName} to typosquatted database, detected via {message}")
            else:
                addPackageToNotCreatedDatabase(modifiedName)
                notCreatedCount += 1
        
        processedPackages = min(i + len(batch), totalPackages)

        print("-----------------------------------------")
        greenText(f"Not created added: {notCreatedCount}")
        redText(f"Typosquatted added: {typosquattedCount}")
        blueText(f"Batch {batchNumber}/{totalBatches} processed.")
        blueText(f"Packages {processedPackages}/{totalPackages} processed.")
        print("-----------------------------------------")

        time.sleep(1)

# def placeholder(modifiedName : str, packageName : str, message : str):
#     if not isPackageInTyposquattedDatabase(modifiedName) and not isPackageInNotCreatedDatabase(modifiedName):
#         print(f"Checking {modifiedName}...")
#         call = checkPackageExists(modifiedName)
#         if call is not False:
#             weeklyDownloads, monthlyDownloads, lastUpdate = call
#             addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, message)
#             redText(f"Added {modifiedName} to typosquatted database, detected via {message}")
#         else:
#             addPackageToNotCreatedDatabase(modifiedName)
#     else:
#         greenText(f"{modifiedName} already in a database, skipping check.")

# Check 1: Levenstein distance 
def levenshteinCheck(packageName: str):
    generated = []

    KEYBOARD_NEIGHBORS = {
        "q": ["w", "a", "s", "1", "2"], 
        "w": ["1", "2", "3", "q", "e", "a", "s", "d"],
        "e": ["2", "3", "4", "w", "r", "s", "d", "f"], 
        "r": ["3", "4", "5", "e", "t", "d", "f", "g"],
        "t": ["4", "5", "6", "r", "y", "f", "g", "h"], 
        "y": ["5", "6", "7", "t", "u", "g", "h", "j"], 
        "u": ["6", "7", "8", "y", "i", "h", "j", "k"], 
        "i": ["7", "8", "9", "u", "o", "j", "k", "l"],
        "o": ["8", "9", "0", "i", "p", "k", "l", ";"], 
        "p": ["o", "l", ";", "'"],

        "a": ["q", "w", "s", "z"], 
        "s": ["w", "e", "a", "d", "z", "x"], 
        "d": ["e", "r", "s", "f", "x", "c"],
        "f": ["r", "t", "d", "g", "c", "v"],
        "g": ["t", "y", "f", "h", "v", "b"], 
        "h": ["y", "u", "g", "j", "b", "n"],
        "j": ["u", "i", "h", "k", "n", "m"], 
        "k": ["i", "o", "j", "l", "m"], 
        "l": ["o", "p", "k"],

        "z": ["a", "s", "x"], 
        "x": ["z", "s", "d", "c"], 
        "c": ["x", "d", "f", "v"], 
        "v": ["c", "f", "g", "b"],
        "b": ["v", "g", "h", "n"], 
        "n": ["b", "h", "j", "m"], 
        "m": ["n", "j", "k"],

        "1": ["2", "q"], 
        "2": ["1", "3", "w"], 
        "3": ["2", "4", "e"], 
        "4": ["3", "5", "r"], 
        "5": ["4", "6", "t"],
        "6": ["5", "7", "y"],
        "7": ["6", "8", "u"], 
        "8": ["7", "9", "i"], 
        "9": ["8", "0", "o"], 
        "0": ["9", "-", "p"],
        "-": ["0", "=", "p"]
    }


    generated.append((packageName + "s", packageName, "Levenshtein distance - added 's'")) # Add an 's' at the end of the package name

    for i in range(len(packageName)):
        modifiedName = packageName[:i] + packageName[i] + packageName[i:]
        generated.append((modifiedName, packageName, "Levenshtein distance - duplicated character")) # Duplicate each character one by one

    for i in range(len(packageName)):
        modifiedName = packageName[:i] + packageName[i+1:]
        generated.append((modifiedName, packageName, f"Levenshtein distance - Remove character")) # Remove each character one by one
    
    for i in range(len(packageName) - 1):
        if packageName[i] == packageName[i+1]:
            continue
        modifiedName = packageName[:i] + packageName[i+1] + packageName[i] + packageName[i+2:]
        generated.append((modifiedName, packageName, f"Levenshtein distance - Swap adjacent characters")) # Swap adjacent characters

    for i, char in enumerate(packageName):
        neighbours = KEYBOARD_NEIGHBORS.get(char, [])
        for neighbour in neighbours:
            modifiedName = packageName[:i] + neighbour + packageName[i+1:]
            if modifiedName != packageName:
                generated.append((modifiedName, packageName, f"Levenshtein distance - Keyboard Proximity")) # Replace with keyboard neighbor

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
    "crypto-", "secure-", "safe-", "auth-", "jwt-", "npmjs-", "github-", "aws-", "azure-", "gcp-",
    "windows-", "mac-", "limux-", "docker-", "plugin-"
    ]

    suffixes = [
    "-js", "-ts", "-node", "-utils", "-helper", "-core", "-service", "-api", "-server", "-cli", "-module",
    "-v1", "-v2", "-v3", "-beta", "-dev", "-next", "-lite", "-min", "-pro", "-plus",
    "-pkg", "-package", "-script", "-lib", "-wrapper", "-official", "-verified", "-secure",
    "-aws", "-azure", "-gcp", "-windows", "-mac", "-linux", "-docker", "-plugin"
    ]

    for prefix in prefixes:
        generated.append((prefix + packageName, packageName, f"Combosquatting - added prefix"))

   
    for suffix in suffixes:
        generated.append((packageName + suffix, packageName, f"Combosquatting - added suffix"))
    
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

def blueText(text):
    print(f"\033[94m{text}\033[0m")

def yellowText(text: str):
    print(f"\033[93m{text}\033[0m")

if __name__ == "__main__":
    packageNamesFromDatabase()