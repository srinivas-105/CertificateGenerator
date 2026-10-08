# Running the Certificate Generation API on Windows

These instructions use Windows PowerShell and do not require Docker.

## 1. Open the project directory

```powershell
cd certificate-generator-api
```

Moves PowerShell into the project folder.

## 2. Create a virtual environment

```powershell
python -m venv .venv
```

Creates an isolated Python environment for the project.

## 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

Activates the environment for the current PowerShell session.

If PowerShell blocks script execution, use this only for the current user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again.

## 4. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

Updates pip before installing project dependencies.

## 5. Install dependencies

```powershell
pip install -r requirements.txt
```

Installs FastAPI, SQLAlchemy, ReportLab, Pytest, and the other required packages.

## 6. Create the environment file

```powershell
Copy-Item .env.example .env
```

Creates the local configuration file used by the application.

## 7. Start the API

```powershell
uvicorn app.main:app --reload
```

Starts the FastAPI development server with automatic reload.

The API is available at:

```text
http://127.0.0.1:8000
```

The first startup creates the SQLite database and generated certificate directory.

## 8. Open Swagger

Open this address in a browser:

```text
http://127.0.0.1:8000/docs
```

Swagger provides an interactive way to test every endpoint.

## 9. Run the tests

Open another PowerShell window, activate the environment, enter the project directory, and run:

```powershell
pytest
```

Runs the complete automated test suite.

## 10. Stop the server

Return to the PowerShell window running Uvicorn and press:

```text
Ctrl+C
```

This stops the development server.
