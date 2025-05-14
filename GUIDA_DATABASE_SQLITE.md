# Guida all'Integrazione di SQLite nella Tua Applicazione Flask "Rossopomodoro Order"

Ciao! Come richiesto, abbiamo integrato un database SQLite nella tua applicazione Flask "Rossopomodoro Order". Questo ti permetterà di gestire gli utenti e le loro credenziali in modo più robusto e flessibile rispetto alle credenziali demo hardcoded.

Abbiamo scelto **SQLite** perché è estremamente semplice da configurare (non richiede un server separato), è perfetto per iniziare e per applicazioni di piccole e medie dimensioni, ed è ben integrato con Flask.

## Modifiche Apportate all'Applicazione:

1.  **Nuove Dipendenze (`requirements.txt`):**
    *   Abbiamo aggiunto `Flask-SQLAlchemy` (per interagire con il database usando oggetti Python) e `Flask-Migrate` (per gestire le modifiche allo schema del database nel tempo).

2.  **Configurazione del Database (`src/main.py`):**
    *   Il file `main.py` è stato aggiornato per inizializzare SQLAlchemy e Flask-Migrate.
    *   Il database SQLite verrà creato come un file chiamato `app.db` all'interno di una cartella `instance` nella directory principale del progetto (`rossopomodoro_flask_app/instance/app.db`).

3.  **Modello Utente (`src/models/user.py`):**
    *   È stato creato un modello `User` che definisce la struttura della tabella degli utenti nel database. Include `id`, `username` (unico) e `password_hash` (la password viene memorizzata in modo sicuro, non in testo semplice).

4.  **Logica di Autenticazione Aggiornata (`src/routes/auth.py`):**
    *   La route `/login` ora verifica le credenziali confrontandole con gli utenti presenti nel database.
    *   È stata aggiunta una nuova route `/register` che permette la creazione di nuovi utenti. Le password vengono automaticamente "hashate" prima di essere salvate.

5.  **Nuovo Template per la Registrazione (`src/templates/register.html`):**
    *   È stata creata una nuova pagina HTML per il form di registrazione.

## Come Inizializzare e Usare il Database (Passaggi Fondamentali):

Per far funzionare il database, dovrai eseguire alcuni comandi la prima volta e ogni volta che modifichi la struttura dei tuoi modelli (tabelle).

1.  **Apri un terminale o prompt dei comandi.**

2.  **Naviga nella cartella principale del progetto:**
    ```bash
    cd percorso/completo/fino/a/rossopomodoro_flask_app
    ```

3.  **Attiva l'ambiente virtuale:**
    *   Su macOS/Linux: `source flask_app_venv/bin/activate`
    *   Su Windows: `flask_app_venv\Scripts\activate`

4.  **Installa/Aggiorna le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Inizializza Flask-Migrate (SOLO LA PRIMA VOLTA):**
    Questo comando crea la cartella `migrations` nel tuo progetto.
    ```bash
    flask db init
    ```

6.  **Crea la Prima Migrazione:**
    Ogni volta che crei un nuovo modello o modifichi un modello esistente (es. aggiungi una colonna), devi creare una "migrazione". Questo comando rileva le modifiche ai tuoi modelli (come la creazione del modello `User`) e genera uno script di migrazione.
    ```bash
    flask db migrate -m "Initial migration with User table"
    ```

7.  **Applica la Migrazione al Database:**
    Questo comando esegue lo script di migrazione, creando effettivamente le tabelle nel tuo file di database `app.db`.
    ```bash
    flask db upgrade
    ```
    Ora il tuo database SQLite (`instance/app.db`) è stato creato e contiene la tabella `user`.

## Come Creare il Primo Utente:

Dopo aver inizializzato il database, puoi creare utenti tramite la pagina di registrazione:

1.  **Avvia l'applicazione Flask (se non è già in esecuzione):**
    ```bash
    python src/main.py
    ```
2.  Apri il browser e vai a `http://127.0.0.1:5000/register`.
3.  Compila il form con un username e una password a tua scelta e clicca su "Register".
4.  Se la registrazione ha successo, verrai reindirizzato alla pagina di login, dove potrai accedere con le credenziali appena create.

## Eseguire l'Applicazione:

Dopo aver inizializzato il database e creato almeno un utente, puoi eseguire l'applicazione come prima:
```bash
python src/main.py
```
Vai su `http://127.0.0.1:5000/` per accedere alla pagina di login.

## Modifiche Future allo Schema del Database:

Se in futuro modifichi il file `src/models/user.py` (o aggiungi nuovi modelli), dovrai ripetere i passaggi 6 e 7 per le migrazioni:

1.  `flask db migrate -m 
