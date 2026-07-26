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
        # Drop the old table to avoid schema conflicts with the new string data
        drop_query = "DROP TABLE IF EXISTS crawl_results"
        
        # Create the updated table
        create_query = """
        CREATE TABLE IF NOT EXISTS crawl_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500) UNIQUE,
            status_code INT,
            response_time_ms INT,
            page_title VARCHAR(500),
            h1_present BOOLEAN,
            meta_desc TEXT,
            has_analytics VARCHAR(255),
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(drop_query)
                await cursor.execute(create_query)
                await conn.commit()
        print("[+] Database schema initialized (fresh table created).")

    # Added meta_desc to the parameters
    async def insert_health_data(self, url, status_code, response_time_ms, page_title, h1_present, meta_desc,has_analytics):
        """Inserts or updates a URL's health and SEO status."""
        if not self.pool:
            return
            
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                    INSERT INTO crawl_results (url, status_code, response_time_ms, page_title, h1_present, meta_desc, crawled_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) AS new_data
                    ON DUPLICATE KEY UPDATE 
                        status_code = new_data.status_code,
                        response_time_ms = new_data.response_time_ms,
                        page_title = new_data.page_title,
                        h1_present = new_data.h1_present,
                        meta_desc = new_data.meta_desc,
                        crawled_at = new_data.crawled_at;
                """
                await cursor.execute(query, (url, status_code, response_time_ms, page_title, h1_present, meta_desc, datetime.datetime.now()))
                await conn.commit()

    async def close(self):
        """Closes the connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("[-] Database connection closed.")