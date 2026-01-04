import sqlite3
import random
import sys
import os
import csv
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the current directory to sys.path to import nscan
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nscan import (
    checkInTyposquattedDB,
    checkInLegitimateDB,
    calculateSuspiciousIndexScore,
    calculateIndexScoreForTyposquatting,
    getWeeklyDownloadsBasic,
    getMonthlyDownloadsBasic,
    getLastUpdate,
    redText,
    greenText,
    yellowText
)

def get_packages_from_db(db_path, table_name, limit=150):
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return []
    
    try:
        connect = sqlite3.connect(db_path)
        cursor = connect.cursor()
        cursor.execute(f"SELECT packageName FROM {table_name}")
        rows = cursor.fetchall()
        connect.close()
        
        packages = [row[0] for row in rows]
        if len(packages) > limit:
            return random.sample(packages, limit)
        return packages
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
        return []

def evaluate_package(packageName):
    print(f"\nEvaluating {packageName}...")
    overallIndexScore = 0
    
    # Logic copied/adapted from nscan.py main()
    if not checkInTyposquattedDB(packageName) and not checkInLegitimateDB(packageName):
        print(f"Package not in database, getting information...")
        weeklyDownloads = getWeeklyDownloadsBasic(packageName)
        monthlyDownloads = getMonthlyDownloadsBasic(packageName)
        
        if weeklyDownloads is None or monthlyDownloads is None:
            print(f"{packageName} does not exist or API error.")
            return None
            
        lastUpdate = getLastUpdate(packageName)
        suspiciousIndexScore = calculateSuspiciousIndexScore(weeklyDownloads, monthlyDownloads, lastUpdate)
        print(f"Suspicious index score: {suspiciousIndexScore}")
        overallIndexScore += suspiciousIndexScore
        
    elif checkInTyposquattedDB(packageName):
        print(f"Found in typosquatted database.")
        packageInfo = checkInTyposquattedDB(packageName)
        # packageInfo structure: (id, packageName, typosquattedFrom, weekly, monthly, lastUpdate, detectionMethods)
        # nscan.py uses indices: originalPackage=2, weekly=3, monthly=4, lastUpdate=5, message=6
        originalPackage = packageInfo[2]
        weeklyDownloads = packageInfo[3]
        monthlyDownloads = packageInfo[4]
        lastUpdate = packageInfo[5]
        message = packageInfo[6]
        
        typosquattingIndexScore = calculateIndexScoreForTyposquatting(originalPackage, weeklyDownloads, monthlyDownloads, lastUpdate, message)
        print(f"Typosquatting index score: {typosquattingIndexScore}")
        overallIndexScore += typosquattingIndexScore
        
    elif checkInLegitimateDB(packageName):
        print(f"Found in legitimate database.")
        # legitimate table structure: (id, packageName, weekly, monthly, lastUpdate)
        # nscan.py uses indices: weekly=2, monthly=3, lastUpdate=4
        packageInfo = checkInLegitimateDB(packageName)
        weeklyDownloads = packageInfo[2]
        monthlyDownloads = packageInfo[3]
        lastUpdate = packageInfo[4]
        print("No index score added.")

    if overallIndexScore >= 10:
        redText(f"Final Score: {overallIndexScore} / 15 (High Risk)")
    elif overallIndexScore > 5:
        yellowText(f"Final Score: {overallIndexScore} / 15 (Medium Risk)")
    else:
        greenText(f"Final Score: {overallIndexScore} / 15 (Low Risk)")
    
    return overallIndexScore

def main():
    # Try to get packages from all three databases to ensure comprehensive testing
    # 100 Legitimate (Should be Low Risk)
    # 100 Typosquatted (Should be High/Medium Risk)
    # 100 Not Created (Should be identified as "does not exist")
    
    legitimate_packages = get_packages_from_db('database/legitimate.db', 'legitimate', 100)
    typosquatted_packages = get_packages_from_db('database/typosquatted.db', 'typosquatted', 100)
    not_created_packages = get_packages_from_db('database/notCreated.db', 'notCreated', 100)
    
    # Create labeled dataset: (packageName, expected_type)
    dataset = []
    for p in legitimate_packages: dataset.append((p, 'legitimate'))
    for p in typosquatted_packages: dataset.append((p, 'typosquatted'))
    for p in not_created_packages: dataset.append((p, 'not_created'))
    
    # If we don't have enough, warn the user
    if len(dataset) < 300:
        print(f"Warning: Only found {len(dataset)} packages to test.")
        print(f"Breakdown: Legitimate={len(legitimate_packages)}, Typosquatted={len(typosquatted_packages)}, NotCreated={len(not_created_packages)}")
    
    # Shuffle them to simulate random input
    random.shuffle(dataset)
    
    # Ensure we have at most 300
    dataset = dataset[:300]
    
    print(f"Starting evaluation on {len(dataset)} packages...")
    
    results = {
        'legitimate': {'total': 0, 'correct': 0}, 
        'typosquatted': {'total': 0, 'correct': 0},
        'not_created': {'total': 0, 'correct': 0}
    }
    
    # Lists to store CSV data
    ground_truth_rows = []
    prediction_rows = []

    for pkg, expected_type in dataset:
        score = evaluate_package(pkg)
        
        # Collect Ground Truth Data
        ground_truth_rows.append([pkg, expected_type])

        # Determine Risk Level string for CSV
        risk_level = "Not Found"
        if score is not None:
            if score >= 10:
                risk_level = "High Risk"
            elif score > 5:
                risk_level = "Medium Risk"
            else:
                risk_level = "Low Risk"
        
        # Collect Prediction Data
        score_str = str(score) if score is not None else "N/A"
        prediction_rows.append([pkg, score_str, risk_level])
        
        is_correct = False
        if expected_type == 'legitimate':
            # Expect Low Risk (<= 5) and must exist (score is not None)
            if score is not None and score <= 5:
                is_correct = True
        elif expected_type == 'typosquatted':
            # Expect Medium/High Risk (> 5) and must exist
            if score is not None and score > 5:
                is_correct = True
        elif expected_type == 'not_created':
            # Expect not found (score is None)
            if score is None:
                is_correct = True
        
        results[expected_type]['total'] += 1
        if is_correct:
            results[expected_type]['correct'] += 1
            
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    
    total_correct = 0
    total_count = 0
    
    for category, stats in results.items():
        if stats['total'] > 0:
            acc = (stats['correct'] / stats['total']) * 100
            print(f"{category.capitalize()}: {stats['correct']}/{stats['total']} ({acc:.2f}%)")
            total_correct += stats['correct']
            total_count += stats['total']
        else:
            print(f"{category.capitalize()}: No samples")
            
    if total_count > 0:
        overall_acc = (total_correct / total_count) * 100
        print("-" * 50)
        print(f"OVERALL ACCURACY: {total_correct}/{total_count} ({overall_acc:.2f}%)")
    print("="*50)

    # Write CSV files
    try:
        with open('ground_truth.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Package Name', 'Ground Truth Label'])
            writer.writerows(ground_truth_rows)
        print(f"\nSaved ground truth data to 'ground_truth.csv'")

        with open('predictions.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Package Name', 'Predicted Score', 'Risk Level'])
            writer.writerows(prediction_rows)
        print(f"Saved prediction data to 'predictions.csv'")
    except Exception as e:
        print(f"Error saving CSV files: {e}")

if __name__ == "__main__":
    main()
