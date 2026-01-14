import requests
import sys
import os

def send_telegram_msg(status):
    token = os.getenv('BOTAPI')
    chat_id = os.getenv('TGID')
    repo = os.getenv('GITHUB_REPOSITORY')
    run_id = os.getenv('GITHUB_RUN_ID')
    
    
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    
    
    if status.lower() == "success":
        emoji = "✅"
        msg_status = "SUCCESS"
    elif status.lower() == "cancelled":
        emoji = "⚠️"
        msg_status = "CANCELLED"
    else:
        emoji = "❌"
        msg_status = "FAILED"

    message_text = (
        f"<b>{emoji} Pipeline {msg_status}</b>\n\n"
        f"<b>Project:</b> {repo}\n"
        f"<b>Link:</b> <a href='{run_url}'>View Workflow Run</a>"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True  
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Notification sent! Status: {msg_status}")
    except Exception as e:
        print(f"Error sending notification: {e}")

if __name__ == "__main__":
    current_status = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    send_telegram_msg(current_status)
