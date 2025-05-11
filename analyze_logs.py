import mysql.connector
from collections import defaultdict

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='rebanta26',
        database='honeypot_db'
    )

def analyze_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all logs
    cursor.execute("SELECT ip, user_agent, accessed_url, timestamp FROM logs")
    logs = cursor.fetchall()

    # Group by IP and User-Agent
    ip_activity = defaultdict(list)
    user_agent_counts = defaultdict(int)

    for log in logs:
        ip = log['ip']
        ua = log['user_agent']
        user_agent_counts[ua] += 1
        ip_activity[ip].append(log)

    print("📊 Top 5 Most Common User-Agents:")
    for ua, count in sorted(user_agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"- {ua} → {count} requests")

    print("\n🔍 Suspicious IPs with High Activity:")
    for ip, entries in ip_activity.items():
        if len(entries) > 10:  # arbitrary threshold
            print(f"- {ip} → {len(entries)} requests")
            suspicious_urls = [entry['accessed_url'] for entry in entries]
            print(f"  URLs: {set(suspicious_urls)}\n")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_logs()