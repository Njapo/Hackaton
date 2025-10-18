# AnimalAI Backend

Python backend for the AnimalAI project using FastAPI, SQLAlchemy, and OpenAI API.

## Features

- 🔐 JWT Authentication with password hashing
- 🐾 Animal management (CRUD operations)
- 🤖 AI-powered animal care advice using OpenAI
- 💾 SQLite database with SQLAlchemy ORM
- 📝 Automatic API documentation with Swagger UI
- ✅ Data validation with Pydantic

## Quick Start

### 1. Setup Virtual Environment

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your settings:
# - Add your OpenAI API key
# - Generate a secure SECRET_KEY (see below)
```

To generate a secure SECRET_KEY:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Run the Application

```powershell
uvicorn app.main:app --reload
```

The API will be available at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Animals
- `GET /api/animals` - Get all animals
- `GET /api/animals/my` - Get current user's animals
- `GET /api/animals/{id}` - Get specific animal
- `POST /api/animals` - Create new animal
- `PUT /api/animals/{id}` - Update animal
- `DELETE /api/animals/{id}` - Delete animal

### AI Features
- `POST /api/ai/ask` - Ask AI about animal care
- `GET /api/ai/history` - Get AI conversation history

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app and routes
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── auth.py              # Authentication & JWT
│   ├── ai_client.py         # OpenAI API client
│   └── utils.py             # Helper functions
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your environment variables (create this)
└── SETUP.md               # Detailed setup instructions
```

## Development

### Running Tests
```powershell
# Install pytest
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Code Quality
```powershell
# Install development tools
pip install black flake8 mypy

# Format code
black app/

# Check code style
flake8 app/

# Type checking
mypy app/
```

## Troubleshooting

**Issue**: PowerShell execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Module not found errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Issue**: OpenAI API errors
- Check your API key in `.env`
- Ensure you have credits in your OpenAI account

**Issue**: Database errors
- Delete `animalai.db` and restart the server to recreate tables

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./animalai.db` |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `APP_NAME` | Application name | `AnimalAI` |
| `APP_VERSION` | Application version | `1.0.0` |
| `DEBUG` | Debug mode | `True` |

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.
