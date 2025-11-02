# Monica API Proxy

Ein einfacher, in Docker verpackter Python-Proxy für die Monica.im API. Ermöglicht das Überschreiben der `/v1/models`-Endpunkt-Antwort mit einer benutzerdefinierten, lokal verwalteten JSON-Datei.

## Features

- Leitet alle Anfragen an `https://openapi.monica.im` weiter.
- Fängt Anfragen an `/v1/models` ab und liefert eine Antwort aus einer lokalen `models.json`-Datei.
- Robuster Fallback auf eine interne Default-Liste, falls `models.json` nicht gefunden wird.
- Einfache Bereitstellung über Docker und Docker Compose.
- Optionale Debug-Ausgaben für die Fehlerbehebung.

## Voraussetzungen

- Docker
- Docker Compose

## Installation & Konfiguration

1.  **Klonen Sie das Repository:**
    ```bash
    git clone https://github.com/DEIN_BENUTZERNAME/DEIN_REPO_NAME.git
    cd DEIN_REPO_NAME
    ```

2.  **Erstellen Sie Ihre Model-Liste:**
    Kopieren Sie die Vorlagedatei und passen Sie sie nach Ihren Wünschen an.
    ```bash
    cp models.example.json models.json
    ```
    Bearbeiten Sie `models.json`, um die gewünschten Modelle aufzulisten.

3.  **Starten Sie den Proxy:**
    ```bash
    docker-compose up -d --build
    ```

Der Proxy ist nun unter `http://localhost:5001` erreichbar.

## Verwendung

Konfigurieren Sie Ihren KI-Client (z.B. LobeChat, Open-WebUI) so, dass er auf die Adresse Ihres Proxy-Servers zeigt:

- **API-Endpunkt:** `http://<IP-DEINES-SERVERS>:5001/v1`
- **API-Key:** Ihr Monica.im API-Key

## Anpassung

Sie können den Host-Port in der `docker-compose.yml`-Datei ändern, falls Port `5001` bereits belegt ist.

