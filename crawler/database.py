import aiomysql
import datetime

class DatabaseManager:
    def __init__(self, host, user, password, db, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.pool = None

    async def connect(self):
        """Creates a connection pool to the MySQL database."""
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            autocommit=True
        )
        print("[+] Connected to MySQL Database.")

    async def init_db(self):
        """Creates the necessary tables if they don't exist."""
        # Updated to include response_time_ms
        query = """
        CREATE TABLE IF NOT EXISTS crawl_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(768) UNIQUE NOT NULL,
            status_code INT NOT NULL,
            response_time_ms INT,
            crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query)
                print("[+] Database schema initialized.")

    # Added response_time_ms to the parameters
    async def insert_health_data(self, url: str, status_code: int, response_time_ms: int):
        """Inserts or updates a URL's health status and response time."""
        # Updated query to handle the new latency parameter and update on duplicate keys
        query = """
        INSERT INTO crawl_results (url, status_code, response_time_ms, crawled_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            status_code = VALUES(status_code), 
            response_time_ms = VALUES(response_time_ms),
            crawled_at = VALUES(crawled_at);
        """
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Appended response_time_ms to the tuple sent to the database
                await cursor.execute(query, (url, status_code, response_time_ms, datetime.datetime.now()))

    async def close(self):
        """Closes the connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("[-] Database connection closed.")