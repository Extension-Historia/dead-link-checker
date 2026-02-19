# This file was compiled by AI for the maintenance of the project "Historia Quick Launcher"

import json
import requests
from requests.exceptions import RequestException
import time

# --- Keyword lists (lowercase matching) ---

KEYWORDS_MOVED = [
    # German
    "wir sind umgezogen",
    "diese seite ist umgezogen",
    "die seite ist umgezogen",
    "seite umgezogen",
    "projekt ist umgezogen",
    "die inhalte finden sie jetzt unter",
    "die inhalte finden sie nun unter",
    "neue adresse",
    "neuer standort",
    "umzug abgeschlossen",

    # English
    "this site has moved",
    "this page has moved",
    "we have moved",
    "this website has moved",
    "content has moved",
    "has been relocated",
    "has moved to",
    "is now located at",
    "new address"
]

KEYWORDS_DISCONTINUED = [
    # German
    "diese seite existiert nicht mehr",
    "angebot wurde eingestellt",
    "seite nicht mehr verfügbar",
    "projekt eingestellt",
    "wird nicht mehr gepflegt",
    "wurde eingestellt",
    "diese webseite wird nicht mehr betreut",

    # English
    "this site is no longer available",
    "this page is no longer available",
    "project has ended",
    "project has been discontinued",
    "no longer maintained",
    "site discontinued",
    "this resource is no longer supported",
    "this page has been archived"
]

HEADERS = {
    "User-Agent": "AcademicLinkChecker/1.0 (+https://example.org)"
}

TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.5


# --- Load data ---

with open("data.json", "r", encoding="utf-8") as f:
    entries = json.load(f)["data"]


results = []


# --- Main loop ---

for entry in entries:
    url = entry.get("link")
    title = entry.get("title")

    record = {
        "title": title,
        "url": url,
        "status": None,
        "details": None
    }

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        text = response.text.lower()

        # HTTP errors
        if response.status_code >= 400:
            record["status"] = "http_error"
            record["details"] = f"HTTP {response.status_code}"

        # Explicit moved messages
        elif any(k in text for k in KEYWORDS_MOVED):
            record["status"] = "moved_notice"
            record["details"] = "page contains relocation message"

        # Discontinued / no longer maintained
        elif any(k in text for k in KEYWORDS_DISCONTINUED):
            record["status"] = "discontinued_notice"
            record["details"] = "page contains discontinuation message"

        # Redirects without explanation
        elif response.history:
            record["status"] = "redirect"
            record["details"] = f"{len(response.history)} redirect(s)"

    except RequestException as e:
        record["status"] = "connection_error"
        record["details"] = e.__class__.__name__

    if record["status"] is not None:
        results.append(record)

    time.sleep(SLEEP_BETWEEN_REQUESTS)


# --- Save results ---

with open("problematic_links.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)


# --- Quick summary ---

summary = {}
for r in results:
    summary[r["status"]] = summary.get(r["status"], 0) + 1

print("Finished.")
for k, v in summary.items():
    print(f"{k}: {v}")
print(f"Total problematic links: {len(results)}")

