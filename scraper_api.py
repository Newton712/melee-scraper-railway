from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_browser():
    chrome_path = shutil.which("google-chrome") or "/usr/bin/google-chrome"
    if not os.path.exists(chrome_path):
        raise RuntimeError("❌ Google Chrome non trouvé. Vérifie ton Dockerfile.")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = chrome_path
    return webdriver.Chrome(options=options)

@app.get("/scrape")
def scrape(url: str = Query(...)):
    try:
        driver = start_browser()
        driver.get(url)

        print("✅ Page chargée")
        print(driver.page_source[:1000])

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.mb-1"))
        )
        tournament_name = driver.find_element(By.CSS_SELECTOR, "h3.mb-1").text.strip()
        tournament_id = url.split("/")[-1]
        raw_date = driver.find_element(By.CSS_SELECTOR, "span[data-toggle='datetime']").get_attribute("data-value").strip()
        dt = datetime.strptime(raw_date, "%m/%d/%Y %I:%M:%S %p") + timedelta(hours=2)
        formatted_date = dt.strftime("%d/%m/%Y %H:%M CEST")

        tournament = {
            "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "tournament_date": formatted_date,
        }

        players = set()
        elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
        for el in elements:
            name = el.get_attribute("innerHTML").split("<svg")[0].strip()
            if name:
                players.add(name)

        rows = driver.find_elements(By.CSS_SELECTOR, "#pairings tbody tr")
        tables = []
        for row in rows:
            try:
                table_num = row.find_element(By.CSS_SELECTOR, "td.TableNumber-column").text.strip()
                ps = row.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
                p1 = ps[0].get_attribute("innerHTML").split("<svg")[0].strip()
                p2 = ps[1].get_attribute("innerHTML").split("<svg")[0].strip()
                tables.append({
                    "round": "Ronde 1",
                    "tableNum": table_num,
                    "player_1": p1,
                    "player_2": p2
                })
            except:
                continue

        driver.quit()

        return {
            "tournament": tournament,
            "players": sorted(players),
            "tables": tables
        }

    except Exception as e:
        print("❌ Erreur:", str(e))
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("scraper_api:app", host="0.0.0.0", port=port)
