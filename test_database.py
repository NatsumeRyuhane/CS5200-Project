import chatgame
from mysql.connector import Error

def test_database_connection():
    try:
        conn = chatgame.get_db_connection()
        if conn.is_connected():
            db_info = conn.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            # List all available databases
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print("Available databases:")
            for db in databases:
                print(f"- {db[0]}")
                
            return True
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")