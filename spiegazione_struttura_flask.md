# Guida alla Tua Applicazione Web Flask "Rossopomodoro Order"

Ciao! Abbiamo trasformato il design del tuo sito Canva "Rossopomodoro Order" in un'applicazione web funzionante utilizzando Python e il framework Flask. Questa guida ti aiuterà a comprendere la struttura del progetto e come puoi gestirlo e modificarlo.

## Struttura del Progetto

L'applicazione è organizzata nella cartella `rossopomodoro_flask_app` con la seguente struttura principale:

```
rossopomodoro_flask_app/
├── flask_app_venv/       # Ambiente virtuale Python (non devi modificarlo direttamente)
├── src/
│   ├── __init__.py       # Rende la cartella 'src' un package Python
│   ├── main.py           # File principale per creare ed eseguire l'app Flask
│   ├── models/           # Cartella per i modelli di database (attualmente vuota)
│   │   └── __init__.py
│   ├── routes/           # Cartella per le "routes" (gli URL dell'applicazione)
│   │   ├── __init__.py
│   │   └── auth.py       # Logica per l'autenticazione (login, logout, pagina di successo)
│   ├── static/           # Cartella per i file statici (CSS, JavaScript, immagini)
│   │   ├── css/
│   │   │   └── custom.css  # Eventuali stili CSS personalizzati aggiuntivi
│   │   │   └── _assets/    # Qui dovrai inserire la cartella _assets estratta da Canva
│   │   ├── js/             # Per i tuoi file JavaScript
│   │   └── images/         # Per le tue immagini
│   └── templates/        # Cartella per i template HTML
│       ├── base.html       # Template HTML di base, ereditato dalle altre pagine
│       ├── login.html      # Template per la pagina di login
│       └── success.html    # Template per la pagina di login riuscito
└── requirements.txt      # File che elenca le dipendenze Python (es. Flask)
```

### Descrizione dei File Chiave:

*   **`rossopomodoro_flask_app/src/main.py`**: È il cuore dell'applicazione. Inizializza l'app Flask e registra i "blueprint" (moduli di route).
*   **`rossopomodoro_flask_app/src/routes/auth.py`**: Contiene la logica per le pagine relative all'autenticazione: la pagina di login (`/login`), la pagina di successo (`/success`) e la funzionalità di logout (`/logout`). Qui sono definite le credenziali demo (`admin`/`password`).
*   **`rossopomodoro_flask_app/src/templates/base.html`**: È un template HTML di base che definisce la struttura comune a tutte le pagine (come l'intestazione, il piè di pagina, e il contenitore principale del contenuto). Le altre pagine (`login.html`, `success.html`) "estendono" questo template.
*   **`rossopomodoro_flask_app/src/templates/login.html`**: Definisce la struttura HTML della pagina di login, inclusi i campi del form.
*   **`rossopomodoro_flask_app/src/templates/success.html`**: Definisce la struttura HTML della pagina visualizzata dopo un login corretto.
*   **`rossopomodoro_flask_app/src/static/`**: Questa cartella conterrà tutti i tuoi file statici. Ho creato sottocartelle per `css`, `js`, e `images`. Dovrai copiare la cartella `_assets` (che contiene i CSS e i font originali del design Canva) all'interno di `src/static/` per far sì che gli stili originali vengano applicati. Ho già predisposto il link al CSS principale di Canva in `base.html`.
*   **`rossopomodoro_flask_app/requirements.txt`**: Elenca le librerie Python necessarie per far funzionare l'applicazione (per ora, solo `Flask`).

## Come Avviare l'Applicazione Localmente

Per eseguire l'applicazione sul tuo computer, dovrai avere Python installato. Segui questi passaggi:

1.  **Apri un terminale o prompt dei comandi.**
2.  **Naviga nella cartella principale del progetto:**
    ```bash
    cd percorso/completo/fino/a/rossopomodoro_flask_app
    ```
3.  **Attiva l'ambiente virtuale:**
    *   Su macOS/Linux:
        ```bash
        source flask_app_venv/bin/activate
        ```
    *   Su Windows:
        ```bash
        flask_app_venv\Scripts\activate
        ```
    Vedrai `(flask_app_venv)` all'inizio della riga del terminale, a indicare che l'ambiente è attivo.
4.  **Installa le dipendenze (se non già fatto o se aggiungi nuove librerie):**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Avvia l'applicazione Flask:**
    ```bash
    python src/main.py
    ```
6.  Apri il tuo browser web e vai all'indirizzo `http://127.0.0.1:5000/` o `http://localhost:5000/`. Dovresti vedere la pagina di login.

## Come Modificare l'Applicazione

### Modificare l'Aspetto (HTML e CSS):

*   **Pagine HTML**: Per modificare il contenuto o la struttura delle pagine, edita i file `.html` nella cartella `src/templates/`.
    *   `login.html`: per la pagina di login.
    *   `success.html`: per la pagina di successo.
    *   `base.html`: per modificare elementi comuni a tutte le pagine (es. il titolo generale del sito nel tag `<title>`, o aggiungere un footer).
*   **Stili CSS**: Gli stili principali sono ereditati dal CSS di Canva. Dovrai:
    1.  **Copiare la cartella `_assets`** (che hai ricevuto con l'estrazione del codice HTML originale da Canva) all'interno della cartella `rossopomodoro_flask_app/src/static/`.
    2.  Il file `base.html` è già configurato per cercare il file CSS principale di Canva in `static/_assets/css/nomefile.css` (il nome esatto del file CSS di Canva è `ea135e019ea51169.css` secondo l'HTML estratto).
    3.  Se vuoi aggiungere stili personalizzati o sovrascrivere quelli di Canva, puoi modificare il file `src/static/css/custom.css` (che è già linkato in `base.html`) o creare nuovi file CSS e linkarli in `base.html`.

### Modificare la Logica di Login:

*   La logica di autenticazione si trova in `src/routes/auth.py`.
*   Attualmente, le credenziali sono fisse: `DEMO_USERNAME = "admin"` e `DEMO_PASSWORD = "password"`.
*   Puoi modificare queste variabili per cambiare le credenziali demo.
*   Per un sistema di login più robusto (es. con utenti da un database), dovresti modificare le funzioni `login()` e, potenzialmente, integrare un database nella cartella `src/models/`.

### Aggiungere Nuove Pagine:

1.  **Crea un nuovo template HTML** in `src/templates/` (es. `nuova_pagina.html`).
2.  **Definisci una nuova route** in `src/routes/auth.py` (o crea un nuovo file di routes, es. `src/routes/general.py`, e registralo come blueprint in `main.py`).
    ```python
    # Esempio in auth.py
    @auth_bp.route("/nuova-pagina")
    def nuova_pagina_route():
        return render_template("nuova_pagina.html")
    ```
3.  Assicurati che il nuovo template HTML estenda `base.html` se vuoi mantenere lo stesso layout.

### Gestire File Statici (Immagini, JS):

*   **Immagini**: Metti le immagini nella cartella `src/static/images/`. Puoi farvi riferimento nei template HTML usando `{{ url_for('static', filename='images/nome_immagine.jpg') }}`.
*   **JavaScript**: Metti i file JavaScript in `src/static/js/`. Puoi linkarli in `base.html` o in template specifici.

## Considerazioni Finali

*   **Chiave Segreta**: In `src/main.py`, la `app.config['SECRET_KEY']` è impostata su un valore di esempio. Per un'applicazione in produzione, dovresti cambiarla con una stringa casuale e segreta.
*   **Modalità Debug**: L'applicazione viene eseguita in modalità debug (`app.run(debug=True)`). Questo è utile per lo sviluppo, ma dovrebbe essere disabilitato per la produzione.
*   **Asset di Canva**: La fedeltà visiva al design originale di Canva dipende dalla corretta inclusione e referenziamento di tutti i file CSS, font e immagini originali presenti nella cartella `_assets`.

Spero che questa guida ti sia utile! Ora hai una base solida per un'applicazione web che puoi espandere e personalizzare.
