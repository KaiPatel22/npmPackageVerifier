import Levenshtein
import sqlite3
from npmCalls import checkPackageExists, getWeeklyDownloads, getMonthlyDownloads, getLastUpdate
from databaseSetup import addPackageToDatabase

def typosquattingDummyFunction():
    print("dummy")


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

def packageNamesFromDatabase():
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT packageName FROM legitimate''')
    rows = cursor.fetchall()
    packageNames = [row[0] for row in rows]
    
    for package in packageNames:
        levenshteinCheck(package)
        homographCheck(package)
        combosquattingCheck(package)


    connect.close()
    return packageNames

def addPackageToTyposqauttedDatabase(packageName: str, typoSquattedFrom : str, weeklyDownloads: int, monthlyDownloads: int, lastUpdate: str, detectionMethods: str):
    connect = sqlite3.connect("database/typosquatted.db")
    cursor = connect.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO typosquatted (packageName, typosquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods)
        VALUES (?, ?, ?, ?, ?, ?)''', (packageName, typoSquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods))
    print(f"Added {packageName} to typosquatted database, detected via {detectionMethods}")
    connect.commit()
    connect.close()

def isPackageInTyposquattedDatabase(packageName: str) -> bool:
    connect = sqlite3.connect("database/typosquatted.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM typosquatted WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0

# Check 1: Levenstein distance 
def levenshteinCheck(packageName: str):
    modifiedName = packageName + "s"
    if not isPackageInTyposquattedDatabase(modifiedName):
        print(f"Checking Levenshtein Distance: {modifiedName}")
        if checkPackageExists(modifiedName) is not False:
            weeklyDownloads, monthlyDownloads, lastUpdate = checkPackageExists(modifiedName)
            addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, "Levenshtein Distance - adding s to end")


# Check 2: Homograph attacks
def homographCheck(packageName : str):
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
        "l": ["Ɩ \u0196", "ӏ \u04CF", "ⅼ \u217C", "Ι \u0399", "l \u006C"],

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
                if not isPackageInTyposquattedDatabase(modifiedName):
                    print(f"Checking homograph attack: {modifiedName}")
                    if checkPackageExists(modifiedName) is not False:
                        weeklyDownloads = getWeeklyDownloads(modifiedName)
                        monthlyDownloads = getMonthlyDownloads(modifiedName)
                        lastUpdate = getLastUpdate(modifiedName)

                        addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, f"Homograph attack - replaced {letter} with {homograph}")


# Check 3: Combosquatting attacks
def combosquattingCheck(packageName : str):
    prefixes = [
    "node-", "js-", "ts-", "ng-", "react-", "vue-", "next-", "express-", "cli-", "utils-", "lib-",
    "crypto-", "secure-", "safe-", "auth-", "jwt-",
    "@types-", "@angular-", "@aws-", "@firebase-", "@google-", "@amazn-", "@goog1e-", "@microsof-",
    "npmjs-", "github-"
    ]

    suffixes = [
    "-js", "-node", "-utils", "-helper", "-core", "-service", "-api", "-server", "-cli", "-module",
    "-v2", "-v3", "-beta", "-dev", "-next", "-lite", "-min", "-pro", "-plus",
    "-pkg", "-package", "-script", "-lib"
    ]

    for prefix in prefixes:
        modifiedName = prefix + packageName
        if not isPackageInTyposquattedDatabase(modifiedName):
            print(f"Checking combosquatting with prefix: {modifiedName}")
            result = checkPackageExists(modifiedName)
            if result is not False:
                weeklyDownloads, monthlyDownloads, lastUpdate = result
                addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, f"Combosquatting - added prefix {prefix}")
   
    for suffix in suffixes:
        modifiedName = packageName + suffix
        if not isPackageInTyposquattedDatabase(modifiedName):
            print(f"Checking combosquatting with suffix: {modifiedName}")
            result = checkPackageExists(modifiedName)
            if result is not False:
                weeklyDownloads, monthlyDownloads, lastUpdate = result
            addPackageToTyposqauttedDatabase(modifiedName, packageName, weeklyDownloads, monthlyDownloads, lastUpdate, f"Combosquatting - added prefix {prefix}")

# Check 4: Hyphen/underscore manipulation 
def hyphenUnderscoreCheck(packageName : str):
    pass


if __name__ == "__main__":
    packageNamesFromDatabase()
