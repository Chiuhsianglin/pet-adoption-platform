# Database Setup Guide

This guide covers the database setup and migration process for the Pet Adoption Platform.

## Prerequisites

1. **Python Environment**: Ensure you have the correct Python environment activated
2. **Dependencies**: Install all required packages with `pip install -r requirements.txt`
3. **MySQL Database**: Have a MySQL database instance running (locally or via Docker)

## Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/pet_adoption
ASYNC_DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/pet_adoption

# Or use individual components
DB_HOST=localhost
DB_PORT=3306
DB_USER=username
DB_PASSWORD=password
DB_NAME=pet_adoption

# Environment
ENVIRONMENT=development
DEBUG=true
```

## Database Migration System

We use Alembic for database migrations, which provides:
- Version control for database schema
- Automatic migration generation
- Safe upgrade/downgrade operations
- Team collaboration support

### Migration Commands

#### 1. Initialize Migration System (Already Done)
```bash
alembic init alembic
```

#### 2. Create Initial Migration
```bash
# Manual migration (recommended for first setup)
alembic revision -m "Initial database schema"

# Auto-generate migration (requires database connection)
alembic revision --autogenerate -m "Migration description"
```

#### 3. Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Apply one migration at a time
alembic upgrade +1
```

#### 4. Rollback Migrations
```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

#### 5. Check Migration Status
```bash
# Show current migration status
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show <revision_id>
```

## Database Schema

The platform uses the following main tables:

### Core Tables
- **users**: User accounts (adopters, shelters, admins)
- **pets**: Pet listings with comprehensive information
- **adoption_applications**: Adoption applications and status
- **chat_rooms**: Communication channels for applications
- **messages**: Chat messages between users
- **notifications**: System and user notifications

### Key Features
- **Enum Types**: Type-safe status and category fields
- **JSON Fields**: Flexible storage for photos, documents, metadata
- **Foreign Keys**: Proper relationships between entities
- **Indexes**: Optimized queries for common operations
- **Timestamps**: Automatic created_at/updated_at tracking

## Development Data Seeding

### Seed Data Overview
The seed system creates realistic development data including:
- **5 Users**: Admin, 2 shelters, 2 adopters
- **5 Pets**: Dogs, cats, and a rabbit with complete profiles
- **2 Applications**: Sample adoption applications in different states
- **Chat Messages**: Sample conversations between users
- **Notifications**: Various notification types

### Running Seed Data
```bash
# Seed database with development data
python manage_db.py seed

# Force seed without confirmation
python manage_db.py seed --force
```

### Seed Data Details

#### Users Created
- **Admin**: admin@petadoption.com (password: admin123)
- **Shelter 1**: shelter1@petadoption.com (password: shelter123)
- **Shelter 2**: shelter2@petadoption.com (password: shelter123)
- **Adopter 1**: adopter1@example.com (password: adopter123)
- **Adopter 2**: adopter2@example.com (password: adopter123)

#### Pets Created
- **Buddy**: Golden Retriever (available)
- **Luna**: Border Collie Mix (available)
- **Whiskers**: Orange Tabby cat (available)
- **Shadow**: Maine Coon cat (pending adoption)
- **Coco**: Holland Lop rabbit (available)

## Production Setup

### 1. Database Creation
```sql
CREATE DATABASE pet_adoption CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'pet_app'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON pet_adoption.* TO 'pet_app'@'%';
FLUSH PRIVILEGES;
```

### 2. Environment Variables
```env
DATABASE_URL=mysql+pymysql://pet_app:secure_password@db_host:3306/pet_adoption
ENVIRONMENT=production
DEBUG=false
```

### 3. Migration Deployment
```bash
# Apply all migrations
alembic upgrade head
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```
**Solution**: Ensure MySQL is running and connection details are correct

#### 2. Import Errors
```
ImportError: No module named 'app.models'
```
**Solution**: Ensure you're in the backend directory and Python path is correct

#### 3. Migration Conflicts
```
alembic.util.exc.CommandError: Multiple heads detected
```
**Solution**: Merge migrations or resolve conflicts manually

#### 4. Pydantic Import Errors
```
PydanticImportError: BaseSettings has been moved to pydantic-settings
```
**Solution**: Install pydantic-settings package: `pip install pydantic-settings`

### Database Management Commands

```bash
# Check database connection
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Initialize database
python manage_db.py init

# Seed development data
python manage_db.py seed

# Reset database (manual table drop required)
python manage_db.py reset
```

## Development Workflow

1. **Start Development**:
   ```bash
   # Start MySQL (via Docker or local)
   docker-compose up -d mysql redis
   
   # Apply migrations
   alembic upgrade head
   
   # Seed development data (optional)
   python manage_db.py seed
   ```

2. **Make Schema Changes**:
   ```bash
   # Modify models in app/models/
   
   # Generate migration
   alembic revision --autogenerate -m "Description of changes"
   
   # Review and edit migration file if needed
   
   # Apply migration
   alembic upgrade head
   ```

3. **Reset Development Database**:
   ```bash
   # Drop all tables (manual or via database tool)
   # Then reapply migrations
   alembic upgrade head
   python manage_db.py seed
   ```

## Best Practices

1. **Always Review Migrations**: Check auto-generated migrations before applying
2. **Backup Before Production**: Always backup production database before migrations
3. **Test Migrations**: Test migrations on staging environment first
4. **Version Control**: Commit migration files to version control
5. **Descriptive Messages**: Use clear, descriptive migration messages
6. **No Direct Schema Changes**: Always use migrations, never modify database directly