# Guida: Deployare l'App Flask con PostgreSQL su Render

Ciao! Come discusso, per deployare la tua applicazione Flask "Rossopomodoro Order" su Render con dati condivisi e persistenti, utilizzeremo un database PostgreSQL ospitato nel cloud. Render stesso offre un servizio di database PostgreSQL facile da integrare.

Ecco i passaggi per configurare tutto:

## 1. Prepara la Tua Applicazione Flask (Modifiche Già Apportate)

Abbiamo già apportato le seguenti modifiche al tuo codice, che sono incluse nei file che ti fornirò:

*   **`requirements.txt` aggiornato:**
    *   Aggiunto `psycopg2-binary` (il driver Python per PostgreSQL).
    *   Aggiunto `gunicorn` (un server WSGI robusto per la produzione, che Render userà per eseguire la tua app).
*   **`src/main.py` aggiornato:**
    *   La configurazione del database (`SQLALCHEMY_DATABASE_URI`) ora cerca una variabile d'ambiente chiamata `DATABASE_URL`. Se la trova (come farà su Render), la usa. Altrimenti, per lo sviluppo locale, usa ancora il file SQLite.
    *   La `SECRET_KEY` dell'app viene letta dalla variabile d'ambiente `SECRET_KEY`.
    *   L'app viene eseguita sulla porta specificata dalla variabile d'ambiente `PORT` (impostata da Render) e con `debug=False`.

## 2. Crea un Database PostgreSQL su Render

1.  **Accedi al tuo account Render.**
2.  Vai alla Dashboard e clicca su **"New +"** e poi seleziona **"PostgreSQL"**.
3.  **Configura il tuo database:**
    *   **Name:** Dai un nome al tuo database (es. `rossopomodoro-db`).
    *   **Region:** Scegli la regione più vicina ai tuoi utenti o a te.
    *   **PostgreSQL Version:** Scegli una versione recente (Render di solito propone l'ultima stabile).
    *   **Plan:** Render offre un **piano gratuito ("Free")** per PostgreSQL che è ottimo per iniziare. Ha delle limitazioni (es. dati cancellati dopo 90 giorni di inattività del database, meno risorse), ma è perfetto per testare e per piccole applicazioni. Seleziona questo se vuoi partire senza costi.
4.  Clicca su **"Create Database"**.
5.  Render impiegherà qualche minuto per creare il database. Una volta pronto, vai alla pagina del tuo nuovo database su Render.
6.  Nella sezione **"Info"** o **"Connect"** del tuo database PostgreSQL su Render, troverai le **credenziali di connessione**. Cerca l'**"Internal Connection String"** o **"External Connection String"**. Questo è l'URL che ci serve. Assomiglierà a qualcosa come `postgres://utente:password@host:porta/nomedb`.
    *   **Importante:** L'applicazione Flask (con SQLAlchemy) si aspetta che l'URL inizi con `postgresql://`. Se Render ti fornisce un URL che inizia con `postgres://`, dovrai cambiarlo in `postgresql://` quando lo imposti come variabile d'ambiente per la tua app (il nostro codice in `main.py` già gestisce questa sostituzione per te!).

## 3. Crea un Nuovo Servizio Web ("Web Service") su Render per la Tua App Flask

1.  Dalla dashboard di Render, clicca su **"New +"** e poi seleziona **"Web Service"**.
2.  **Collega il tuo repository Git:** Scegli il repository dove hai il codice della tua applicazione Flask (es. GitHub, GitLab).
3.  **Configura il servizio web:**
    *   **Name:** Dai un nome al tuo servizio web (es. `rossopomodoro-app`).
    *   **Region:** Scegli la stessa regione del tuo database, se possibile.
    *   **Branch:** Seleziona il branch del tuo repository da deployare (es. `main` o `master`).
    *   **Root Directory:** Lascia vuoto se il file `requirements.txt` e la cartella `src` sono nella root del repository, altrimenti specifica il percorso.
    *   **Runtime:** Render dovrebbe rilevare Python automaticamente. Seleziona la versione di Python che stai usando (es. Python 3.11).
    *   **Build Command:** Render di solito suggerisce `pip install -r requirements.txt`. Questo è corretto.
    *   **Start Command:** Qui devi dire a Render come avviare la tua applicazione usando Gunicorn. Inserisci:
        ```
        gunicorn src.main:app
        ```
        (Questo dice a Gunicorn di cercare l'oggetto `app` nel file `src/main.py`).
    *   **Plan:** Scegli il piano per il tuo servizio web. Render ha un piano **"Free"** anche per i Web Services, con limitazioni (es. l'app va in sleep dopo inattività, meno risorse). È ottimo per iniziare.

4.  **Imposta le Variabili d'Ambiente:**
    *   Prima di cliccare su "Create Web Service", scorri verso il basso fino alla sezione **"Environment"** o **"Advanced" -> "Environment Variables"**.
    *   Clicca su **"Add Environment Variable"** (o "Add Secret File" se preferisci per valori sensibili, ma per `DATABASE_URL` una variabile d'ambiente normale va bene).
    *   Aggiungi le seguenti variabili:
        *   **Key:** `DATABASE_URL`
            **Value:** Incolla qui l'**Internal Connection String** del tuo database PostgreSQL che hai copiato da Render. Ricorda: se inizia con `postgres://`, il nostro codice in `main.py` lo convertirà in `postgresql://`.
        *   **Key:** `SECRET_KEY`
            **Value:** Genera una stringa lunga, casuale e segreta. Puoi usare un generatore di password online o crearne una tu. Esempio: `super_secret_random_string_for_flask_app` (USA UNA TUA CHIAVE UNICA E SICURA!).
        *   **Key:** `PYTHON_VERSION` (Opzionale, ma buona pratica)
            **Value:** La versione di Python che stai usando (es. `3.11.0`).

5.  Clicca su **"Create Web Service"**.

## 4. Deploy e Migrazioni del Database

1.  Render inizierà a fare il build e il deploy della tua applicazione. Puoi seguire i log del deploy.
2.  **Eseguire le Migrazioni del Database (Passaggio Cruciale):**
    Una volta che l'app è deployata (o anche durante il primo build se configurato correttamente), devi creare le tabelle nel tuo database PostgreSQL cloud. Con SQLite, lo facevi localmente. Con un database cloud, devi dire a Render di eseguire i comandi di migrazione.
    *   **Opzione 1: Usare la Console di Render (One-off Job):**
        *   Una volta che il tuo servizio web è attivo (anche se potrebbe fallire all'inizio se il database non ha tabelle), vai alla pagina del tuo servizio web su Render.
        *   Cerca la sezione **"Shell"** o **"Console"**.
        *   Render potrebbe usare un "Build Shell" o una "Runtime Shell". Idealmente, vuoi una shell nell'ambiente dove la tua app è in esecuzione con le variabili d'ambiente impostate.
        *   Esegui i comandi di migrazione Flask:
            ```bash
            flask db init  # Esegui SOLO SE non hai MAI inizializzato le migrazioni per questo progetto
            flask db migrate -m "Initial cloud migration"
            flask db upgrade
            ```
        *   **Nota:** `flask db init` crea la cartella `migrations`. Se l'hai già nel tuo repository Git, non dovresti rieseguirlo a meno che tu non stia partendo da zero con le migrazioni su Render. Se la cartella `migrations` è già nel tuo codice, esegui solo `migrate` e `upgrade`.
    *   **Opzione 2: Aggiungere comandi di migrazione al Build Script (Avanzato e con Cautela):**
        *   Potresti modificare il **Build Command** su Render per includere `flask db upgrade` dopo `pip install`. Esempio: `pip install -r requirements.txt && flask db upgrade`. Questo applicherà le migrazioni ad ogni build. Fai attenzione con questo approccio in produzione, specialmente se hai migrazioni che potrebbero fallire o richiedere intervento manuale.
    *   **Opzione 3: Connettersi Remotamente (Più Complesso):**
        *   Potresti usare uno strumento client PostgreSQL (come `psql` o pgAdmin) per connetterti al tuo database Render usando l'**External Connection String** e applicare gli schemi manualmente o tramite script. Questo è generalmente più complesso per le migrazioni gestite da Flask-Migrate.

    **Per iniziare, l'Opzione 1 (usare la Console di Render) è spesso la più diretta per il primo setup.**

## 5. Testa la Tua Applicazione

*   Una volta che l'app è deployata e le migrazioni del database sono state applicate, vai all'URL pubblico della tua applicazione fornito da Render (qualcosa come `https://nome-tua-app.onrender.com`).
*   Prova a registrarti con un nuovo utente e a fare il login. I dati dovrebbero ora essere salvati nel database PostgreSQL su Render e essere persistenti.

## Considerazioni Aggiuntive:

*   **Piani Gratuiti di Render:** Ricorda le limitazioni dei piani gratuiti (sleep per inattività, risorse limitate, dati del DB cancellati dopo 90 giorni di inattività del DB). Per un'applicazione di produzione seria, dovrai considerare i piani a pagamento.
*   **Log:** Controlla sempre i log della tua applicazione e del database su Render per diagnosticare eventuali problemi.
*   **Variabili d'Ambiente per lo Sviluppo Locale:** Per continuare a sviluppare localmente con SQLite mentre usi PostgreSQL su Render, il codice in `main.py` che abbiamo preparato gestisce già questo fallback (se `DATABASE_URL` non è impostata, usa SQLite). Potresti voler usare un file `.env` per gestire le variabili d'ambiente localmente (e aggiungerlo a `.gitignore`).

Seguendo questi passaggi, dovresti essere in grado di deployare la tua applicazione Flask con un database PostgreSQL condiviso e persistente su Render!

