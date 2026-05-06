import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# --- CONFIGURATION ---
NB_PAGES = 700  # number of pages to scrape
CSV_FILE = "hellowork_all_offers.csv"


def run_scraper_all_offers():
    print(f"🤖 Démarrage du scraping : {NB_PAGES} pages (TOUTES les offres)")

    # --- Chrome options ---
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-search-engine-choice-screen")

    # --- Driver ---
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_offers = []

    try:
        for page in range(1, NB_PAGES + 1):
            print(f"\n📄 Page {page}/{NB_PAGES}")

            # URL without any keyword or location
            url = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?p={page}"
            driver.get(url)

            # --- Cookies (only first page) ---
            if page == 1:
                time.sleep(4)
                try:
                    driver.find_element(By.ID, "hw-cc-notice-accept-btn").click()
                    print("🍪 Cookies accepted")
                except:
                    pass
            else:
                time.sleep(random.uniform(5, 8))

            # --- Wait page load ---
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("⚠️ Page not loaded")
                continue

            # --- Parse page ---
            soup = BeautifulSoup(driver.page_source, "html.parser")

            for li in soup.find_all("li"):
                link = li.find("a", href=True)
                if not link:
                    continue

                text = li.get_text(" ", strip=True)
                if len(text) < 20:
                    continue

                title_tag = li.find(["h3", "h4", "span"])
                title = title_tag.get_text(strip=True) if title_tag else "Sans titre"

                url_offre = link["href"]
                if not url_offre.startswith("http"):
                    url_offre = "https://www.hellowork.com" + url_offre

                all_offers.append({
                    "Titre": title,
                    "Description_Brute": text[:300],
                    "Lien": url_offre,
                    "Page_Source": page
                })

            print(f"✅ Offres cumulées : {len(all_offers)}")

    except Exception as e:
        print(f"❌ Erreur : {e}")

    finally:
        driver.quit()
        print("\n🛑 Fin du scraping")

        if all_offers:
            df = pd.DataFrame(all_offers)
            df.drop_duplicates(subset=["Lien"], inplace=True)

            df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
            print(f"💾 Fichier sauvegardé : {CSV_FILE}")
            print(f"📊 Total offres uniques : {len(df)}")
        else:
            print("❌ Aucune donnée récupérée")


if __name__ == "__main__":
    run_scraper_all_offers()
