import sqlite3


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

print(sum_downloads_under_threshold())