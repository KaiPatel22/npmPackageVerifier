# npmPackageVerifier

## How to enter the virtual environment:
Mac:
    
    source myenv/bin/activate

Windows: 
    
    myenv\Scripts\activate

## How to run the nscan tool as a path variable 
Mac:

    chmod +x nscan
    
    code/nscan.py install <package name>


## Used for getting the top npm packages
https://github.com/wooorm/npm-high-impact

## How to set up Database 

Ensure you have created a folder called "database" in the root directory for this project 

Run: 
    npm install npm-high-impact

Then run:
    python code/populateDatabase.py 

The python file should create a database called "legitimate.db" in the database folder and you should see print statements stating the packages have been added to the database. 

Additional:
https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer <- Use SQLite Viewer VSCode extension to be able to open the database in a readable format.