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

malicious = [
    "acorns", "acorn-node", "express-ajv", "js-argparse", "brace-expansion-cli", 
    "js-camelcase", "chalkk", "chalks", "chalk-node", "chalk-helper", "chalk-lite", 
    "ng-chalk", "color-names", "node-commander", "react-commander", "github-commander", 
    "ng-commander", "commander-js", "commander-core", "debugs", "debugg", "vue-debug", 
    "debug-js", "debug-module", "execa-pro", "js-form-data", "form-data-js", 
    "secure-fs-extra", "fs-extra-plus", "ts-glob", "utils-glob", "glob-plus", 
    "node-globals", "globals-package", "iconv-lite-cli", "ignores", "ignores-cli", 
    "node-inherits", "inherits-js", "ts-is-number", "is-number", "js-isarray", 
    "js-yaml-cli", "express-json5", "json5-utils", "js-lru-cache", "lib-lru-cache", 
    "lru-cache-plus", "mime-db-lite", "mkdirps", "mkdirp-lite", "mss", "react-ms", 
    "ms-lib", "onetime-cli", "ts-pify", "next-postcss", "postcss-utils", "postcss-v2", 
    "punycode-cli", "js-qs", "react-qs", "vue-js", "qs-cli", "react-is-dev", 
    "node-readable-stream", "resolves", "ts-resolve", "vue-resolve", "resolve-cli", 
    "rimraff", "ts-schema-utils", "ng-semver", "semver-node", "semver-next", 
    "react-slash", "slash-cli", "source-maps", "source-map-next", "strip-bom-cli", 
    "support-color-cli", "tslib-cli", "js-typescript", "cli-typescript", "typescript-api", 
    "typescript-dev", "typescript-next", "typescript-helper", "uuids", "ts-uuid", 
    "uuid-node", "uuid-pro", "uuid-lib", "which-server", "wss", "react-ws", 
    "secure-ws", "ws-api", "ws-cli", "ts-yargs", "yargs-lite", "ws-server",
]

suspicious = [
    "acorn-node", "ajv-cli", "chalk-cli", "safe-commander", "commander-plus", 
    "ts-debug", "escape-string-regexp-node", "safe-execa", "find-up-cli", 
    "react-form-data", "express-form-data", "form-data-utils", "form-data-lite", 
    "node-fs-extra", "globs", "node-glob", "cli-glob", "glob-utils", "glob-cli", 
    "js-yml-lite", "lru-cache-plus", "make-dir-cli", "path-exists-cli", "postcss-js", 
    "postcss-cli", "ts-punycode", "qss", "node-resolve", "safe-resolve", "resolve-pkg", 
    "resolve-package", "semver-utils", "express-slash", "source-map-js", "source-map-cli", 
    "strip-ansi-cli", "strip-json-comments-cli", "typescript-node", "typescript-service", 
    "node-uuid", "js-uuid", "react-uuid", "vue-uuid", "uuid-js", "node-which", 
    "while-module", "next-ws", "express-ws"
]


finalArray = ["express","react","vue","angular","lodash","moment","axios","chalk","debug","nodemon",
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
    "eslint-plugin-react","eslint-plugin-jsx-a11y", "acorns", "acorn-node", "express-ajv", "js-argparse", "brace-expansion-cli", 
    "js-camelcase", "chalkk", "chalks", "chalk-node", "chalk-helper", "chalk-lite", 
    "ng-chalk", "color-names", "node-commander", "react-commander", "github-commander", 
    "ng-commander", "commander-js", "commander-core", "debugs", "debugg", "vue-debug", 
    "debug-js", "debug-module", "execa-pro", "js-form-data", "form-data-js", 
    "secure-fs-extra", "fs-extra-plus", "ts-glob", "utils-glob", "glob-plus", 
    "node-globals", "globals-package", "iconv-lite-cli", "ignores", "ignores-cli", 
    "node-inherits", "inherits-js", "ts-is-number", "is-number", "js-isarray", 
    "js-yaml-cli", "express-json5", "json5-utils", "js-lru-cache", "lib-lru-cache", 
    "lru-cache-plus", "mime-db-lite", "mkdirps", "mkdirp-lite", "mss", "react-ms", 
    "ms-lib", "onetime-cli", "ts-pify", "next-postcss", "postcss-utils", "postcss-v2", 
    "punycode-cli", "js-qs", "react-qs", "vue-js", "qs-cli", "react-is-dev", 
    "node-readable-stream", "resolves", "ts-resolve", "vue-resolve", "resolve-cli", 
    "rimraff", "ts-schema-utils", "ng-semver", "semver-node", "semver-next", 
    "react-slash", "slash-cli", "source-maps", "source-map-next", "strip-bom-cli", 
    "support-color-cli", "tslib-cli", "js-typescript", "cli-typescript", "typescript-api", 
    "typescript-dev", "typescript-next", "typescript-helper", "uuids", "ts-uuid", 
    "uuid-node", "uuid-pro", "uuid-lib", "which-server", "wss", "react-ws", 
    "secure-ws", "ws-api", "ws-cli", "ts-yargs", "yargs-lite", "ws-server", "acorn-node", "ajv-cli", "chalk-cli", "safe-commander", "commander-plus", 
    "ts-debug", "escape-string-regexp-node", "safe-execa", "find-up-cli", 
    "react-form-data", "express-form-data", "form-data-utils", "form-data-lite", 
    "node-fs-extra", "globs", "node-glob", "cli-glob", "glob-utils", "glob-cli", 
    "js-yml-lite", "lru-cache-plus", "make-dir-cli", "path-exists-cli", "postcss-js", 
    "postcss-cli", "ts-punycode", "qss", "node-resolve", "safe-resolve", "resolve-pkg", 
    "resolve-package", "semver-utils", "express-slash", "source-map-js", "source-map-cli", 
    "strip-ansi-cli", "strip-json-comments-cli", "typescript-node", "typescript-service", 
    "node-uuid", "js-uuid", "react-uuid", "vue-uuid", "uuid-js", "node-which", 
    "while-module", "next-ws", "express-ws"]

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


print(f"length of finalArray: {len(finalArray)}, length of legitimate: {len(npm_packages)}, length of malicious: {len(malicious)}, length of suspicious: {len(suspicious)}")