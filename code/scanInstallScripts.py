import json
import os
import re
import subprocess
import tempfile
import platform
from dataclasses import dataclass
from typing import List, Dict

'''
This file is used to check if the package has any malicious or suspicious install scripts within the post or pre install hooks. 
'''

'''
Creates a class to hold the install script information
'''
@dataclass
class ScriptInfo:
    scriptName: str
    pattern: str
    description: str
    severity: int

class ScriptScanner:
    INSTALL_SCRIPTS = {"preinstall", "install", "postinstall"}


    def __init__(self, packageName: str):
        self.rules = self.loadRules()
        self.packageName = packageName

    def loadRules(self):
        """
        Heuristic rule set
        Severity: 1 (low) -> 5 (critical)
        """
        return [
            {
                "pattern": r"curl\s+.*\|\s*sh", # Checks for curls commands or commands that end in .sh indiciating a shell script
                "description": "Downloads and executes remote shell script",
                "severity": 5,
            },
            {
                "pattern": r"wget\s+.*\|\s*sh", # Checks for wget commands or commands that end in .sh indiciating a shell script
                "description": "Downloads and executes remote shell script",
                "severity": 5,
            },
            {
                "pattern": r"base64\s+(-d|--decode)",
                "description": "Base64 decoding (possible obfuscation)",
                "severity": 4,
            },
            {
                "pattern": r"eval\s*\(",
                "description": "Dynamic code execution via eval",
                "severity": 4,
            },
            {
                "pattern": r"fromCharCode",
                "description": "Character code obfuscation",
                "severity": 3,
            },
            {
                "pattern": r"(process\.env|ENV\[)",
                "description": "Access to environment variables",
                "severity": 3,
            },
            {
                "pattern": r"(uname|whoami|id)",
                "description": "System fingerprinting",
                "severity": 2,
            },
            {
                "pattern": r"powershell",
                "description": "PowerShell execution (Windows-specific)",
                "severity": 4,
            },
        ]
    
    def installPackage(self, workdir: str):
        if platform.system() == "Windows":
            subprocess.run(
                ["npm.cmd", "init", "-y"],
                cwd=workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        else:
            subprocess.run(
                ["npm", "init", "-y"],
                cwd=workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

        if platform.system() == "Windows":
            subprocess.run(
                ["npm.cmd", "install", self.packageName, "--ignore-scripts"],
                cwd=workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        else:
            subprocess.run(
                ["npm", "install", self.packageName, "--ignore-scripts"],
                cwd=workdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
    
    def extractScripts(self, workdir: str) -> Dict[str, str]:
        jsonPath = os.path.join(
            workdir, "node_modules", self.packageName, "package.json"
        )

        if not os.path.exists(jsonPath):
            return {}
        
        with open(jsonPath, "r", encoding="utf-8") as f:
            json_ = json.load(f)

        scripts = json_.get("scripts", {})
        return {
            name: cmd
            for name, cmd in scripts.items()
            if name in self.INSTALL_SCRIPTS
        }
    
    def scanScripts(self, scripts: Dict[str, str]) -> List[ScriptInfo]:
        findings = []

        for scriptName, scriptCMD in scripts.items():
            for rule in self.rules:
                if re.search(rule["pattern"], scriptCMD, re.IGNORECASE):
                    findings.append(
                        ScriptInfo(
                            scriptName=scriptName,
                            pattern=rule["pattern"],
                            description=rule["description"],
                            severity=rule["severity"],
                        )
                    )
    
        return findings
    
    def scanPackage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                self.installPackage(tmpdir)
                scripts = self.extractScripts(tmpdir)
                findings = self.scanScripts(scripts)
            except subprocess.CalledProcessError as e: # if the script fails to install with "--ignore-scripts", we assume it is malicious
                info = ScriptInfo(
                            scriptName="install",
                            pattern="npm install failure",
                            description="Package failed to install without executing scripts",
                            severity=5,
                        )
                print(f"Installation failed for package {self.packageName}, marking as risky.")
                return {
                    "package": self.packageName,
                    "scriptsFound": [],
                    "findings": [info],
                    "riskScore": 5,
                }
        
        riskScore = sum(f.severity for f in findings)

        if riskScore > 0:
            print(f"Installation Scripts found for package {self.packageName}:")
            for finding in findings:
                print(
                    f"- Script: {finding.scriptName}, pattern: {finding.pattern}, "
                    f"description: {finding.description}, severity: {finding.severity}"
                )
        else:
            print(f"No risky installation scripts found for package {self.packageName}.")
        
        return {
            "package": self.packageName,
            "scriptsFound": list(scripts.keys()),
            "findings": findings,
            "riskScore": riskScore,
        }


