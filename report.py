import asyncio
import aiomysql
import sys
import csv
import datetime

async def generate_report():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Me@448262',
        'db': 'sitepulse_db'
    }
    
    print("\n========================================")
    print("      SITEPULSE DIAGNOSTIC REPORT       ")
    print("========================================\n")
    print("[*] Connecting to database...")
    
    try:
        async with aiomysql.create_pool(**db_config) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    print("[+] Connected successfully!\n")
                    
                    # --- UPDATED: Added has_analytics to the SELECT query ---
                    await cursor.execute("""
                        SELECT url, status_code, response_time_ms, page_title, h1_present, meta_desc, has_analytics 
                        FROM crawl_results
                    """)
                    results = await cursor.fetchall()
                    
        if not results:
            print("No data found in the database. Run the crawler first!")
            return
            
        total_pages = len(results)
        broken_links = [row for row in results if row['status_code'] >= 400]
        slowest_pages = sorted(
            [row for row in results if row['response_time_ms'] is not None], 
            key=lambda x: x['response_time_ms'], 
            reverse=True
        )[:5]
        
        ready_pages = []
        flagged_pages = []
        
        for row in results:
            issues = []
            
            if row['status_code'] != 200:
                issues.append(f"Bad Status: {row['status_code']}")
                
            if row['response_time_ms'] is None or row['response_time_ms'] > 3000 or row['response_time_ms'] == 0:
                time_val = row['response_time_ms'] if row['response_time_ms'] is not None else "Unknown"
                issues.append(f"High Latency/Timeout: {time_val}ms")
                
            if row['page_title'] == 'Missing Title' or not row['page_title']:
                issues.append("Missing <title>")
                
            if not row['h1_present']:
                issues.append("Missing <h1>")
                
            if row['meta_desc'] == 'Missing' or not row['meta_desc']:
                issues.append("Missing <meta> description")
                
            # --- UPDATED: Flag pages missing crucial PPC tracking pixels ---
            if row['has_analytics'] == 'None' or not row['has_analytics']:
                issues.append("Missing Tracking Pixels")

            if issues:
                row['issues'] = issues
                flagged_pages.append(row)
            else:
                ready_pages.append(row)
                
        print(f"Total Pages Analyzed: {total_pages}")
        
        if total_pages > 0:
            health_score = ((total_pages - len(broken_links)) / total_pages) * 100
            print(f"Site Health Score:    {health_score:.1f}%")
        
        print("\n--- BROKEN LINKS ---")
        if broken_links:
            for link in broken_links:
                print(f"[{link['status_code']}] {link['url']}")
        else:
            print("Perfect! No broken links found.")
            
        print("\n--- TOP 5 SLOWEST PAGES ---")
        if slowest_pages:
            for page in slowest_pages:
                print(f"{page['response_time_ms']} ms - {page['url']}")
        else:
            print("No response time data available.")
            
        print("\n========================================")
        print("  PPC LANDING PAGE AUDIT (SEO & SPEED)  ")
        print("========================================\n")
        
        print(f"✅ FULLY OPTIMIZED & READY ({len(ready_pages)} URLs)")
        print("-" * 40)
        
        print(f"⚠️ NEEDS ATTENTION ({len(flagged_pages)} URLs)")
        print("-" * 40)
        for page in flagged_pages:
            print(f"URL: {page['url']}")
            print(f"Issues: {', '.join(page['issues'])}")
            print("-" * 30)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ppc_audit_{timestamp}.csv"
        
        print(f"\n[*] Exporting data to {filename}...")
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # --- UPDATED: Added 'Tracking Pixels' to headers ---
            writer.writerow(['URL', 'Status Code', 'Speed (ms)', 'Page Title', 'Meta Description', 'H1 Present', 'Tracking Pixels', 'Readiness', 'Issues to Fix'])
            
            for page in ready_pages:
                writer.writerow([
                    page['url'], 
                    page['status_code'], 
                    page['response_time_ms'], 
                    page['page_title'], 
                    page['meta_desc'], 
                    page['h1_present'], 
                    page['has_analytics'],  # --- UPDATED ---
                    'Ready', 
                    'None'
                ])
                
            for page in flagged_pages:
                writer.writerow([
                    page['url'], 
                    page['status_code'], 
                    page['response_time_ms'], 
                    page['page_title'], 
                    page['meta_desc'], 
                    page['h1_present'],
                    page['has_analytics'],  # --- UPDATED ---
                    'Needs Attention', 
                    ' | '.join(page['issues'])
                ])
                
        print(f"[+] Export complete! Check your project folder for '{filename}'\n")

    except Exception as e:
        print(f"[-] Database connection failed: {repr(e)}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_report())