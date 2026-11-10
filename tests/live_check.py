"""Live Gemini check for Zehn — uses the registered surrogate
credential (key never handled, never printed). Calls the real
zehn.gemini functions once each and validates the outputs with
the engine validators. Run: python tests/live_check.py
"""
import os
import sys

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dynamic_credentials import dynamic_credential_entry  # noqa: E402

entry = dynamic_credential_entry("custom.google-gemini")
os.environ["GEMINI_API_KEY"] = entry["surrogate"]

from zehn import gemini  # noqa: E402

print("key_available:", gemini.key_available())

tip, err = gemini.daily_tip("roman", "memory 82, speed 54, 12 games")
if err:
    print("TIP ERROR:", err)
    sys.exit(1)
print(f"TIP OK: {tip['words']} words, language={tip['language']}")
print("tip first 120 chars:", tip["tip"][:120].replace("\n", " "))
assert tip["words"] >= 10 and tip["ai"] is True

summ, err = gemini.weekly_summary(
    "roman", "12 games, best skill memory 82, weakest speed 54")
if err:
    print("SUMMARY ERROR:", err)
    sys.exit(1)
print(f"SUMMARY OK: {summ['words']} words, language={summ['language']}")
print("summary first 120 chars:",
      summ["summary"][:120].replace("\n", " "))
assert summ["words"] >= 15 and summ["ai"] is True
print("LIVE CHECK PASSED")
