import requests
import argparse
import traceback
import json
import os
from flask import Flask, request, jsonify, Response
from waitress import serve

# Globale Variable für den Debug-Status
DEBUG_MODE = False

def log(message):
    """Gibt eine Nachricht nur aus, wenn der Debug-Modus aktiviert ist."""
    if DEBUG_MODE:
        print(message)

# 1. Initialisieren der Flask-Anwendung
app = Flask(__name__)

# 2. Die Ziel-URL
TARGET_URL = "https://openapi.monica.im"

# 3. Lade die Model-Liste aus einer externen JSON-Datei
# ------------------- ANFANG DER ÄNDERUNG -------------------

# Der Pfad zur Konfigurationsdatei IM INNEREN des Containers.
MODELS_FILE_PATH = '/app/models.json'

# Standard-Antwort, falls die Datei nicht gefunden wird oder fehlerhaft ist.
# Dies ist jetzt die ursprüngliche, vollständige Liste.
DEFAULT_MODELS_RESPONSE = {
    "data": [
        {"id": "gpt-5"}, {"id": "gpt-4o"}, {"id": "gpt-4o-mini"},
        {"id": "gpt-4-5"}, {"id": "gpt-4.1"}, {"id": "gpt-4.1-mini"},
        {"id": "gpt-4.1-nano"}, {"id": "claude-sonnet-4-5"},
        {"id": "claude-4-sonnet"}, {"id": "claude-4-sonnet-thinking"},
        {"id": "claude-4-opus"}, {"id": "claude-4-opus-thinking"},
        {"id": "claude-opus-4-1-20250805-thinking"},
        {"id": "claude-3-7-sonnet-thinking"}, {"id": "claude-3-7-sonnet"},
        {"id": "claude-3-5-sonnet"}, {"id": "claude-3-5-haiku"},
        {"id": "gemini-2.5-pro"}, {"id": "gemini-2.5-flash"},
        {"id": "gemini-2.0-flash"}, {"id": "gemini-1"},
        {"id": "o1-preview"}, {"id": "o3"}, {"id": "o3-mini"},
        {"id": "o4-mini"}, {"id": "deepseek-reasoner"},
        {"id": "deepseek-chat"}, {"id": "deepclaude"}, {"id": "sonar"},
        {"id": "sonar-reasoning-pro"}, {"id": "grok-3-beta"},
        {"id": "grok-4"}, {"id": "grok-code-fast-1"}
    ]
}

# Initialisiere MODELS_RESPONSE mit dem Default.
# Wenn das Laden aus der Datei fehlschlägt, bleibt dieser Wert erhalten.
MODELS_RESPONSE = DEFAULT_MODELS_RESPONSE

try:
    # Versuche, die JSON-Datei zu öffnen und zu laden.
    with open(MODELS_FILE_PATH, 'r', encoding='utf-8') as f:
        # Wenn das Laden erfolgreich ist, wird die Variable überschrieben.
        MODELS_RESPONSE = json.load(f)
    print(f"INFO: Model-Liste erfolgreich aus {MODELS_FILE_PATH} geladen.")
except FileNotFoundError:
    print(f"WARNUNG: Model-Datei {MODELS_FILE_PATH} nicht gefunden. Verwende die interne Default-Liste.")
except json.JSONDecodeError:
    print(f"FEHLER: Model-Datei {MODELS_FILE_PATH} enthält ungültiges JSON. Verwende die interne Default-Liste.")
except Exception as e:
    print(f"FEHLER: Unerwarteter Fehler beim Laden von {MODELS_FILE_PATH}: {e}. Verwende die interne Default-Liste.")

# ------------------- ENDE DER ÄNDERUNG -------------------

@app.route('/v1/models', methods=['GET'])
def get_models():
    log("Anfrage an /v1/models empfangen. Antwort wird gesendet.")
    return jsonify(MODELS_RESPONSE)

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    try:
        url = f"{TARGET_URL}/{path}"
        log(f"Leite Anfrage weiter: {request.method} {url}")

        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        data = request.get_data()
        
        log(f"Empfangene Bytes (Request Body): {len(data)}")

        try:
            resp = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                data=data,
                stream=True,
                timeout=120
            )

            if resp.status_code != 200:
                print(f"WARNUNG: Antwort von {request.method} {url} erhielt Status-Code {resp.status_code}")

            log(f"Antwort von {url} erhalten mit Status-Code: {resp.status_code}")

            def stream_with_logging():
                total_bytes = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        total_bytes += len(chunk)
                    yield chunk
                log(f"Gesendete Bytes (Response Body): {total_bytes}")
            
            response = Response(stream_with_logging(), status=resp.status_code)
            
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            for name, value in resp.headers.items():
                if name.lower() not in excluded_headers:
                    response.headers[name] = value
            
            return response

        except requests.exceptions.RequestException as e:
            print(f"FEHLER: Verbindung zum Zielserver {url} fehlgeschlagen: {e}")
            return jsonify({"error": f"Proxy request failed: {e}"}), 502

    except Exception as e:
        log(f"Ein unerwarteter interner Fehler ist aufgetreten: {e}")
        if DEBUG_MODE:
            traceback.print_exc()
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ein robuster Proxy für die Monica.im API.")
    parser.add_argument('--port', type=int, default=5001,
                        help='Der Port, auf dem der Proxy-Server laufen soll (Standard: 5001).')
    parser.add_argument('--debug', action='store_true',
                        help='Aktiviert die Ausgabe von Debug-Informationen in der Konsole.')
    
    args = parser.parse_args()

    if args.debug:
        DEBUG_MODE = True

    port = args.port
    
    print(f"Monica.im Production Proxy wird auf http://0.0.0.0:{port} gestartet...")
    if DEBUG_MODE:
        print("Debug-Modus ist aktiviert.")
    
    serve(app, host='0.0.0.0', port=port, threads=8)

