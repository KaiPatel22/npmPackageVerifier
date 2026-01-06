# ...existing code...
import sqlite3
from pathlib import Path
from npmCalls import checkBulkPackageExists

npm_packages = [
    "express","react","vue","angular","lodash","moment","axios","chalk","debug","nodemon",
    "eslint","prettier","webpack","babel-core","typescript","rxjs","jest","mocha","chai","sinon",
    "jquery","sass","tailwindcss","bootstrap","next","nuxt","gatsby","react-router","redux",
    "redux-thunk","body-parser","cors","dotenv","mongoose","sequelize","graphql","apollo-server",
    "socket.io","passport","jsonwebtoken","bcrypt","helmet","morgan","rimraf","mkdirp","yargs",
    "commander","ora","inquirer","figlet","uuid","validator","date-fns","fastify","pino","winston",
    "concurrently","cross-env","esm","ts-node","@babel/preset-env","@babel/plugin-transform-runtime",
    "@types/node","@types/react","stylelint","postcss","sass-loader","cssnano","imagemin","sharp",
    "gulp","grunt","parcel-bundler","rollup","browserify","postman-request","web3","ethers","three",
    "animejs","chart.js","d3","leaflet","fullcalendar","quill","prosemirror","jest-cli","supertest",
    "cypress","puppeteer","playwright","selenium-webdriver","firebase","aws-sdk","googleapis","stripe",
    "twilio","nodemailer","@types/express","@types/jest","eslint-config-airbnb","eslint-plugin-import",
    "eslint-plugin-react","eslint-plugin-jsx-a11y",
]

def package(packageName: str) -> bool:
    connect = sqlite3.connect("database/legitimate.db")
    cursor = connect.cursor()
    cursor.execute('''SELECT COUNT(*) FROM legitimate WHERE packageName = ?''', (packageName,))
    count = cursor.fetchone()[0]
    connect.close()
    return count > 0

count = 0 
for pkg in npm_packages:
    exists = package(pkg)
    print(f"Package: {pkg}, Exists in DB: {exists}")
    if exists:
        count += 1
print(f"Total packages found in DB: {count} out of {len(npm_packages)}")


print(checkBulkPackageExists(npm_packages))

