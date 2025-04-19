# TitleTrail

## Project Overview
TitleTrail is a Django-based backend application with a frontend for managing RTC documents and property details.

---

## Backend Setup

### 1. Create a Virtual Environment
Navigate to the `backend` folder and create a virtual environment:
```bash
cd backend
python3 -m venv venv
```

Activate the virtual environment:
- On Linux/Mac:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Ensure the `.env` file is in the root directory (`/home/tejas/TitleTrail`) and contains the following:
```env
DEBUG=True
DATABASE_NAME=your-local-database-name
DATABASE_USER=your-local-database-user
DATABASE_PASSWORD=your-local-database-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
OPENAI_API_KEY=your-openai-api-key
```

### 4. Run Migrations
Apply the database migrations to set up the schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Optional)
To access the Django admin panel, create a superuser:
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
Start the Django development server:
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`.

---

## Frontend Setup

### 1. Navigate to the Frontend Folder
Go to the `frontend` folder:
```bash
cd frontend
```

### 2. Install Dependencies
Install the required dependencies:
```bash
npm install
```

### 3. Start the Frontend Development Server
Run the following command to start the Vite development server:
```bash
npm run dev
```

The frontend will typically run on `http://localhost:5173`.

---
