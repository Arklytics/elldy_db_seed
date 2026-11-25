# Elldy DB Seed Project

A small Django + MySQL project for generating large datasets to test Elldy Brick.

## 1. Open in VS Code

Open this project folder in VS Code and open a PowerShell terminal.

## 2. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

> If `mysqlclient` fails to install on Windows, install PyMySQL instead:
>
> ```powershell
> pip install pymysql
> ```
>
> Then add this to `config/__init__.py`:
>
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

## 4. Create MySQL database

From Windows terminal:

```powershell
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE elldy_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Exit MySQL:

```sql
exit;
```

## 5. Set your MySQL password

Either edit `config/settings.py` or set environment variables in PowerShell:

```powershell
$env:MYSQL_DATABASE="elldy_test"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="YOUR_PASSWORD"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
```

## 6. Create the table

```powershell
python manage.py makemigrations
python manage.py migrate
```

## 7. Seed data

### 1 lakh rows

```powershell
python manage.py seed_transactions --rows 100000
```

### 5 lakh rows

```powershell
python manage.py seed_transactions --rows 500000
```

### 10 lakh / 1 million rows

```powershell
python manage.py seed_transactions --rows 1000000
```

### Delete existing rows first and create a fresh 5 lakh

```powershell
python manage.py seed_transactions --rows 500000 --clear
```

You can change batch size if needed:

```powershell
python manage.py seed_transactions --rows 500000 --batch-size 10000
```

## 8. Verify count

```powershell
python manage.py shell
```

Then:

```python
from dataapp.models import Transaction
Transaction.objects.count()
```

## 9. Elldy Brick connection

If Brick and MySQL run on this same Windows PC:

- Host: `127.0.0.1`
- Port: `3306`
- Database: `elldy_test`
- Username: your MySQL user
- Password: your MySQL password
- Table: `transactions`

For production-style testing, create a dedicated read-only MySQL user instead of using root.
