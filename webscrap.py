import requests
from bs4 import BeautifulSoup
import re
import json
import time

class TNAUFieldPlantScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        self.base_url = "https://agritech.tnau.ac.in/crop_protection/"
        self.master_dataset = []
        
        # High-Priority Field Plant Indices
        self.indices = {
            "Rice": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_insectpest%20_cereals_paddymain.html",
            "Cotton": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_insectpest%20_cottonmain.html",
            "Sugarcane": "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop_insectpest%20_sugarcanemain.html"
        }

    def get_links(self, index_url):
        """Extracts all specific pest/disease page links from a main index."""
        try:
            r = requests.get(index_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                # Target links that look like detail pages
                if any(k in a['href'] for k in ['_m', 'insectpest', 'disease']):
                    full_url = requests.compat.urljoin(index_url, a['href'])
                    links.append(full_url)
            return list(set(links))
        except: return []

    def extract_features(self, url, crop_name):
        """Parses a detail page into structured columns using Regex anchors."""
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text(separator=" ").strip()

            # Define regex logic for columns (Features)
            # We look for keywords and grab text until the next known header
            headers = ["Symptoms of damage", "Identification", "Management", "ETL", "Cultural", "Chemical"]
            
            def get_section(start_keyword, end_keywords):
                pattern = rf"{start_keyword}.*?[:\n](.*?)(?={'|'.join(end_keywords)}|$)"
                match = re.search(pattern, text, re.S | re.I)
                return match.group(1).strip() if match else "N/A"

            # Scientific Name extraction (usually follows a colon in the first few lines)
            sci_name_match = re.search(r":\s*([A-Z][a-z]+\s[a-z]+)", text[:500])

            data = {
                "Crop": crop_name,
                "Common_Name": soup.find('title').text.split(":")[0].strip() if soup.find('title') else "Unknown",
                "Scientific_Name": sci_name_match.group(1) if sci_name_match else "N/A",
                "Symptoms": get_section("Symptom", ["Identification", "Management", "ETL"]),
                "Identification": get_section("Identification", ["Management", "ETL", "Symptom"]),
                "ETL": get_section("ETL", ["Management", "Cultural", "Chemical"]),
                "Management_Methods": get_section("Management", ["Home", "About Us", "Contact"]),
                "Source_URL": url
            }
            return data
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def run(self):
        for crop, url in self.indices.items():
            print(f"--- Processing {crop} ---")
            sub_links = self.get_links(url)
            print(f"Found {len(sub_links)} links for {crop}")
            
            for link in sub_links:
                page_data = self.extract_features(link, crop)
                if page_data:
                    self.master_dataset.append(page_data)
                    print(f"Scraped: {page_data['Common_Name']}")
                time.sleep(1) # Ethical scraping delay

        # Final Save
        with open('plant_data_columns.json', 'w', encoding='utf-8') as f:
            json.dump(self.master_dataset, f, indent=4, ensure_ascii=False)
        print(f"Success! {len(self.master_dataset)} entries saved.")

if __name__ == "__main__":
    scraper = TNAUFieldPlantScraper()
    scraper.run()