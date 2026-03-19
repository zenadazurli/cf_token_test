#!/usr/bin/env python3
# cf_token_test.py - Test ottenimento CF Token su Render

import requests
import json
import base64
import time
import sys
from datetime import datetime

# ==================== CONFIGURAZIONE ====================
BROWSERLESS_TOKEN = "2UB77nckQfSpg8veaa27f3b03f6b4b02075815526a7afd992"
BQL_URL = f"https://production-sfo.browserless.io/chrome/bql?token={BROWSERLESS_TOKEN}&stealth=true&proxy=residential&proxyCountry=it"

SITE_URL = "https://www.easyhits4u.com/?join_popup_show=1"
# ========================================================

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

def get_cf_token():
    log("=" * 70)
    log("🔑 BROWSERQL - OTTIENI CF TOKEN")
    log("=" * 70)
    log(f"🇮🇹 Proxy residenziale ITALIA")
    log(f"🛡️ Stealth mode attivo")

    query = """
    mutation {
      goto(url: "%s", waitUntil: networkIdle) {
        status
        url
      }
      
      solve(type: cloudflare, timeout: 30000) {
        found
        solved
        token
        time
      }
      
      screenshot(fullPage: true) {
        base64
      }
    }
    """ % SITE_URL

    payload = {"query": query}
    headers = {"Content-Type": "application/json"}

    try:
        log("\n📡 Invio richiesta...")
        response = requests.post(
            BQL_URL,
            json=payload,
            headers=headers,
            timeout=120  # Timeout più lungo per Render
        )

        log(f"📊 Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                log("\n❌ ERRORI:")
                for error in data["errors"]:
                    log(f"   - {error.get('message')}")
                return False

            result = data.get("data", {})

            # Info navigazione
            goto_info = result.get("goto", {})
            log(f"\n🌐 URL: {goto_info.get('url')}")
            log(f"📊 Status: {goto_info.get('status')}")

            # TOKEN
            solve_info = result.get("solve", {})
            if solve_info.get("solved"):
                token = solve_info.get("token")
                log("\n" + "=" * 70)
                log("✅✅✅ CF TOKEN OTTENUTO!")
                log("=" * 70)
                log(f"🔑 Token: {token[:100]}...")
                log(f"📏 Lunghezza: {len(token)}")
                
                # Salva token
                with open(f"cf_token_{int(time.time())}.txt", "w") as f:
                    f.write(token)
                log(f"💾 Token salvato")
                
                return True
            else:
                log("\n❌ Token non ottenuto")
                log(f"   Trovato: {solve_info.get('found')}")
                
            # Screenshot
            screenshot_data = result.get("screenshot", {}).get("base64")
            if screenshot_data:
                filename = f"page_{int(time.time())}.png"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(screenshot_data))
                log(f"\n📸 Screenshot: {filename}")

        else:
            log(f"❌ Errore HTTP: {response.status_code}")
            log(f"Risposta: {response.text[:500]}")

    except Exception as e:
        log(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def main():
    log("🚀 Avvio test CF Token su Render...")
    success = get_cf_token()
    
    if success:
        log("\n✅ TEST COMPLETATO CON SUCCESSO")
        # Tieni il container vivo per debug
        log("⏳ Container attivo per 60 secondi...")
        time.sleep(60)
    else:
        log("\n❌ TEST FALLITO")
        time.sleep(30)
    
    log("🔚 Chiusura")

if __name__ == "__main__":
    main()
