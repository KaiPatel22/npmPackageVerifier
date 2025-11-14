import Levenshtein


def typosquattingDummyFunction():
    print("dummy")

# Check 1: Levenstein distance 
def levenshteinCheck(packageName: str):
    listOfNewNames = []
    listOfNewNames.append(packageName + "s")
    listOfNewNames.append(packageName + packageName[-1])
    listOfNewNames.append(packageName.strip(-1))
    
    print(listOfNewNames)


levenshteinCheck("Kai")
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
    
    for character in packageName:
        if character in HOMOGRAPH_MAP:
            dodgyChars = HOMOGRAPH_MAP[character]
            for dodgyChar in dodgyChars:
                


# Check 3: Combosquatting attacks
def combosquattingCheck(packageName : str):
    pass

# Check 4: Hyphen/underscore manipulation 
def hyphenUnderscoreCheck(packageName : str):
    pass
