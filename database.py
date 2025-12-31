"""
Database connection and management module
Handles MySQL connections and provides connection pooling
"""

import mysql.connector
from mysql.connector import pooling
from config import get_config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config = get_config()

# Create connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="booking_pool",
        pool_size=5,
        pool_reset_session=True,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )
    logger.info("Database connection pool created successfully")
except mysql.connector.Error as err:
    logger.error(f"Error creating connection pool: {err}")
    connection_pool = None


def get_db_connection():
    """
    Get a database connection from the pool
    
    Returns:
        connection: MySQL connection object
        None: If connection fails
    """
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
            return connection
        else:
            # Fallback to direct connection if pool not available
            connection = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            return connection
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        return None


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Execute a database query with proper error handling
    
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for parameterized query
        fetch (bool): Whether to fetch results
        fetch_one (bool): Whether to fetch only one result
    
    Returns:
        Result of query execution or None on error
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid if cursor.lastrowid else True
        
        return result
        
    except mysql.connector.Error as err:
        logger.error(f"Query execution error: {err}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        if connection:
            connection.rollback()
        return None
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def init_database():
    """
    Initialize database tables if they don't exist
    This is useful for first-time setup
    """
    
    tables = {
        'users': """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'staff') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'facilities': """
            CREATE TABLE IF NOT EXISTS facilities (
                facility_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                capacity INT NOT NULL,
                status ENUM('active', 'inactive') DEFAULT 'active',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'bookings': """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                facility_id INT NOT NULL,
                booking_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                status ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
                purpose TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (facility_id) REFERENCES facilities(facility_id) ON DELETE CASCADE,
                INDEX idx_date_facility (booking_date, facility_id),
                INDEX idx_status (status)
            )
        """
    }
    
    try:
        for table_name, create_query in tables.items():
            result = execute_query(create_query)
            if result is not None:
                logger.info(f"Table '{table_name}' created or already exists")
            else:
                logger.error(f"Failed to create table '{table_name}'")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False


def check_database_connection():
    """
    Check if database connection is working
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    connection = get_db_connection()
    if connection and connection.is_connected():
        connection.close()
        return True
    return False


def test_database():
    """
    Comprehensive database test with detailed output
    """
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)
    
    # Show configuration (without password)
    print(f"\n📋 Configuration:")
    print(f"   Host: {config.DB_HOST}")
    print(f"   Port: {config.DB_PORT}")
    print(f"   User: {config.DB_USER}")
    print(f"   Database: {config.DB_NAME}")
    print(f"   Password: {'*' * 8}")
    
    try:
        print("\n🔄 Testing connection...")
        
        connection = get_db_connection()
        
        if not connection or not connection.is_connected():
            print("❌ Connection failed!")
            print("\n🔧 Troubleshooting:")
            print("   1. Check if MySQL service is running")
            print("   2. Verify password in .env file")
            print("   3. Make sure database 'booking_system' exists")
            print("=" * 70)
            return False
        
        print("✅ Connection successful!")
        
        cursor = connection.cursor(dictionary=True)
        
        # Get MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"\n📊 MySQL Version: {version['VERSION()']}")
        
        # Get current database
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        print(f"📊 Current Database: {db['DATABASE()']}")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📁 Tables found: {len(tables)}")
        
        if len(tables) == 0:
            print("⚠️  No tables found. Initializing database...")
            cursor.close()
            connection.close()
            if init_database():
                print("✅ Database tables created successfully")
                # Reconnect to show tables
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
        
        for table in tables:
            table_name = list(table.values())[0]
            print(f"   ✓ {table_name}")
            
            # Count records in each table
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()
            print(f"     └─ Records: {count['count']}")
        
        # Show users
        cursor.execute("SELECT user_id, name, email, role FROM users")
        users = cursor.fetchall()
        
        if len(users) > 0:
            print(f"\n👥 Users in database ({len(users)}):")
            for user in users:
                print(f"   • {user['name']} ({user['email']}) - {user['role']}")
        else:
            print("\n⚠️  No users found. You may need to insert sample data.")
        
        # Show facilities
        cursor.execute("SELECT facility_id, name, capacity, status FROM facilities")
        facilities = cursor.fetchall()
        
        if len(facilities) > 0:
            print(f"\n🏢 Facilities in database ({len(facilities)}):")
            for facility in facilities:
                print(f"   • {facility['name']} - Capacity: {facility['capacity']} - {facility['status']}")
        else:
            print("\n⚠️  No facilities found. You may need to insert sample data.")
        
        # Show bookings count
        cursor.execute("SELECT COUNT(*) as count FROM bookings")
        bookings = cursor.fetchone()
        print(f"\n📅 Total bookings: {bookings['count']}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED! Database is ready to use.")
        print("=" * 70)
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ DATABASE ERROR!")
        print(f"Error: {err}")
        print("\n🔧 Common solutions:")
        print("   1. Check MySQL service: Get-Service MySQL*")
        print("   2. Verify .env file exists and has correct password")
        print("   3. Create database: CREATE DATABASE booking_system;")
        print("=" * 70)
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"Error: {e}")
        print("=" * 70)
        return False


# Test connection when module is run directly
if __name__ == "__main__":
    test_database()