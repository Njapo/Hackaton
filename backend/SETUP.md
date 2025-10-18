# AnimalAI Backend Setup Instructions

## Prerequisites
- Python 3.8 or higher installed
- VS Code with Python extension

## Setup Steps

### 1. Create Virtual Environment

Open a terminal in VS Code and navigate to the backend folder:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

### 2. Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error, run this first:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

### 3. Install Required Packages

Once the virtual environment is activated, install all dependencies:

```powershell
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv openai passlib[bcrypt] python-jose[cryptography]
```

Or use the requirements.txt file:

```powershell
pip install -r requirements.txt
```

### 4. Create Environment Variables

Copy the `.env.example` file to `.env` and fill in your actual values:

```powershell
cp .env.example .env
```

Edit `.env` with your actual API keys and configuration.

### 5. Run the Application

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

API documentation will be available at: http://localhost:8000/docs

## Verify Installation

Check installed packages:

```powershell
pip list
```

## Deactivate Virtual Environment

When you're done working:

```powershell
deactivate
```

## Troubleshooting

- **PowerShell execution policy error**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Package installation fails**: Make sure you're in the activated virtual environment
- **Module not found errors**: Ensure all packages are installed and venv is activated
