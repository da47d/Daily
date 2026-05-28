import os
import json
import xml.etree.ElementTree as ET
import requests

def get_raw_news():
    print("Hole aktuelle Schlagzeilen...")
    feeds = [
        "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml",
        "https://search.yahoo.com/mrss/archive/techcrunch"
    ]
    headlines = []
    for url in feeds:
        try:
            response = requests.get(url, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:12]:
                title = item.find('title').text
                desc = item.find('description').text if item.find('description') is not None else ""
                headlines.append(f"Titel: {title}\nInhalt: {desc}\n---")
        except Exception as e:
            print(f"Fehler bei Feed {url}: {e}")
    return "\n".join(headlines)

def generate_news_with_ai(raw_text):
    print("Rufe Gemini-KI auf...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY fehlt in den Umgebungsvariablen!")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    Du bist der Redakteur für ein minimalistisches Cyberpunk-Dashboard. 
    Hier sind aktuelle Roh-Nachrichten:
    {raw_text}
    
    Erstelle daraus genau 5 prägnante Nachrichten im JSON-Format.
    - 3 für die Kategorie "global" (Globale Wirtschaft, Märkte, Makro)
    - 2 für die Kategorie "vc" (Startups, Tech-Investments, VC)
    
    Jede Nachricht MUSS exakt dieses Format haben:
    {{
        "tag": "EIN_KURZE_TAG_IN_GROSSBUCHSTABEN",
        "headline": "Eine knackige Schlagzeile auf Deutsch",
        "summary": "1-2 Sätze Zusammenfassung der Relevanz."
    }}
    
    Gib AUSSCHLIESSLICH das reine JSON-Objekt zurück. Keine Markdown-Formatierung, kein ```json.
    Struktur:
    {{
        "global": [ ... 3 items ... ],
        "vc": [ ... 2 items ... ]
    }}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    text_response = result['candidates'][0]['content']['parts'][0]['text']
    return text_response.strip()

if __name__ == "__main__":
    raw_data = get_raw_news()
    if raw_data:
        try:
            ai_json_text = generate_news_with_ai(raw_data)
            
            # Sicherheits-Netz: Falls die KI doch Markdown-Codeblöcke mitschickt, schneiden wir sie ab
            if ai_json_text.startswith("```"):
                ai_json_text = ai_json_text.split("```json")[-1].split("```")[0].strip()
                
            parsed_json = json.loads(ai_json_text)
            
            with open("news.json", "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=2)
            print("news.json erfolgreich aktualisiert!")
        except Exception as e:
            print(f"Fehler: {e}")
