import sqlite3
import random


def sum_downloads_under_threshold(
	db_path: str = "database/typosquatted.db",
	table: str = "typosquatted",
	weekly_limit: int = 1000,
	monthly_limit: int = 1000,
) -> tuple[int, int]:
	"""Sum weekly and monthly downloads across all packages.

	A package's weekly downloads contribute to the weekly sum only when
	`weeklyDownloads < weekly_limit`. Similarly, a package's monthly downloads
	contribute to the monthly sum only when `monthlyDownloads < monthly_limit`.

	Returns:
		(weekly_sum, monthly_sum)
	"""

	if weekly_limit < 0 or monthly_limit < 0:
		raise ValueError("weekly_limit and monthly_limit must be non-negative")

	# Avoid SQL injection via table name.
	if not table.isidentifier():
		raise ValueError(f"Invalid table name: {table!r}")

	query = f"""
		SELECT
			COALESCE(SUM(CASE WHEN weeklyDownloads < ? THEN weeklyDownloads ELSE 0 END), 0) AS weekly_sum,
			COALESCE(SUM(CASE WHEN monthlyDownloads < ? THEN monthlyDownloads ELSE 0 END), 0) AS monthly_sum
		FROM {table}
	"""

	connect = sqlite3.connect(db_path)
	try:
		cursor = connect.cursor()
		weekly_sum, monthly_sum = cursor.execute(query, (weekly_limit, monthly_limit)).fetchone()
		return int(weekly_sum), int(monthly_sum)
	finally:
		connect.close()


def get_suspicious_high_download_packages(
	db_path: str = "database/typosquatted.db",
	table: str = "typosquatted",
	weekly_threshold: int = 1000,
	monthly_threshold: int = 5000,
) -> list[dict]:
	"""Get typosquatted packages with suspiciously high downloads.

	Returns packages where either weeklyDownloads >= weekly_threshold 
	OR monthlyDownloads >= monthly_threshold.

	Args:
		db_path: Path to the SQLite database
		table: Table name to query
		weekly_threshold: Minimum weekly downloads to be considered suspicious
		monthly_threshold: Minimum monthly downloads to be considered suspicious

	Returns:
		List of dictionaries containing package information:
		[{
			'packageName': str,
			'typosquattedFrom': str,
			'weeklyDownloads': int,
			'monthlyDownloads': int,
			'lastUpdate': str,
			'detectionMethods': str
		}, ...]
	"""

	if weekly_threshold < 0 or monthly_threshold < 0:
		raise ValueError("weekly_threshold and monthly_threshold must be non-negative")

	# Avoid SQL injection via table name.
	if not table.isidentifier():
		raise ValueError(f"Invalid table name: {table!r}")

	query = f"""
		SELECT packageName, typosquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods
		FROM {table}
		WHERE weeklyDownloads >= ? OR monthlyDownloads >= ?
		ORDER BY monthlyDownloads DESC, weeklyDownloads DESC
	"""

	connect = sqlite3.connect(db_path)
	try:
		cursor = connect.cursor()
		rows = cursor.execute(query, (weekly_threshold, monthly_threshold)).fetchall()
		
		suspicious_packages = [
			{
				'packageName': row[0],
				'typosquattedFrom': row[1],
				'weeklyDownloads': row[2],
				'monthlyDownloads': row[3],
				'lastUpdate': row[4],
				'detectionMethods': row[5]
			}
			for row in rows
		]
		
		return suspicious_packages
	finally:
		connect.close()


def get_malicious_low_download_packages(
	db_path: str = "database/typosquatted.db",
	table: str = "typosquatted",
	weekly_max: int = 1000,
	monthly_max: int = 5000,
) -> list[dict]:
	"""Get typosquatted packages with low downloads (likely malicious).

	Returns packages where BOTH weeklyDownloads < weekly_max 
	AND monthlyDownloads < monthly_max.

	Args:
		db_path: Path to the SQLite database
		table: Table name to query
		weekly_max: Maximum weekly downloads (exclusive)
		monthly_max: Maximum monthly downloads (exclusive)

	Returns:
		List of dictionaries containing package information:
		[{
			'packageName': str,
			'typosquattedFrom': str,
			'weeklyDownloads': int,
			'monthlyDownloads': int,
			'lastUpdate': str,
			'detectionMethods': str
		}, ...]
	"""

	if weekly_max < 0 or monthly_max < 0:
		raise ValueError("weekly_max and monthly_max must be non-negative")

	# Avoid SQL injection via table name.
	if not table.isidentifier():
		raise ValueError(f"Invalid table name: {table!r}")

	query = f"""
		SELECT packageName, typosquattedFrom, weeklyDownloads, monthlyDownloads, lastUpdate, detectionMethods
		FROM {table}
		WHERE weeklyDownloads < ? AND monthlyDownloads < ?
		ORDER BY monthlyDownloads ASC, weeklyDownloads ASC
	"""

	connect = sqlite3.connect(db_path)
	try:
		cursor = connect.cursor()
		rows = cursor.execute(query, (weekly_max, monthly_max)).fetchall()
		
		malicious_packages = [
			{
				'packageName': row[0],
				'typosquattedFrom': row[1],
				'weeklyDownloads': row[2],
				'monthlyDownloads': row[3],
				'lastUpdate': row[4],
				'detectionMethods': row[5]
			}
			for row in rows
		]
		
		return malicious_packages
	finally:
		connect.close()


if __name__ == "__main__":
	print("Sum of downloads under threshold:")
	print(sum_downloads_under_threshold())
	
	print("\nMalicious low-download typosquatted packages:")
	malicious = get_malicious_low_download_packages(weekly_max=1000, monthly_max=5000)
	print(f"Found {len(malicious)} malicious packages")
	
	# Randomly select 300 packages
	sample_size = min(300, len(malicious))
	random_sample = random.sample(malicious, sample_size)
	random_package_names = [pkg['packageName'] for pkg in random_sample]
	
	print(f"\n\nRandomly selected {sample_size} malicious package names:")
	print(random_package_names)