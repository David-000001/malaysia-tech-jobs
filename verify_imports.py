import sys
print("Python Version:", sys.version)

try:
    import database.connection
    print("[OK] Database connection module imported successfully.")
except Exception as e:
    print("[FAIL] Database connection import failed:", e)

try:
    import scraper.base_scraper
    import scraper.hiredly_scraper
    import scraper.jobstreet_scraper
    import scraper.mock_scraper
    print("[OK] Scraper modules imported successfully.")
except Exception as e:
    print("[FAIL] Scraper import failed:", e)

try:
    import nlp.resume_processor
    print("[OK] NLP resume processor imported successfully.")
except Exception as e:
    print("[FAIL] NLP import failed:", e)

try:
    import analytics.visualizer
    print("[OK] Analytics visualizer imported successfully.")
except Exception as e:
    print("[FAIL] Analytics import failed:", e)

print("\n--- System check completed ---")
