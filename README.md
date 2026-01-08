# npmPackageVerifier

This tool aims to reduce the number of malicious npm packages downloaded by first running some preliminary security checks. We have taken the top 5688 legitimate packages (based on number of downloaded and number of packages that depend on this package to rank importance), from these we have generated typosquatted package names from commonly used typosquatting techniques, we then used batch processing to keep track of if the packages exists or not, if they do, they are added to a typosquatted database along with their package information and if they don't exist the package name is added to a notCreated database (typosquatting.db). The second check we do is for checking install scripts within the pre and post hooks (scanInstallScripts.py). In the main implementation of the scanner, we assign index scores based on the typosquatting technique used, download counts, last update and also assign an index score based on if malicious install scripts are found. When the tool is called, then package is first checked to see if it is in a database, if it is the package information is queried directly from the database and if not the package information is retrieved using an API call and a standard check on the download counts and last update is ran. The tool then shows why it added index score and a final status indicated by colour e.g. green for safe, yellow for suspicious and red for malicious. After the analytics have been shown, the user is then prompted to see if they want to continue to install/update.

# IMPORTANT: Please ensure the libraries in requirements.txt have been installed using 
    pip install -r requirements.txt

## How to enter the virtual environment (if its been created):
Mac:
    
    source myenv/bin/activate

Windows: 
    
    myenv\Scripts\activate

## How to run the nscan tool
    python code/nscan.py install <package name> || python code/nscan.py update <package name>

## How to set up Database (before running tool) - NOT needed if database/ has 'legitimate.db', 'notCreated.db' and 'typosquatted.db'

Ensure you have created a folder called "database" in the root directory for this project 

Run: 
    
    npm install npm-high-impact

Then run:
    
    python code/populateDatabase.py - Populates the legitimate database

    python code/typosquatting.py - Populates the typosquatted and notCreated db


## Used for getting the top npm packages
https://github.com/wooorm/npm-high-impact

## Additional:
https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer <- SQLite Viewer VSCode extension to be able to open the database in a readable format.