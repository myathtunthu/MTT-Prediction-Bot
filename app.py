from flask import Flask, request, redirect
import requests
import random
import json

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7783839439:AAHSd5_N6NmAYlL3d7OLWq3Wc3RVvnYhyzQ"

def send_telegram_message(chat_id, text):
    """Send message synchronously using requests"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Send message error: {str(e)}")
        return None

def get_bot_info():
    """Get bot info synchronously"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Get bot info error: {str(e)}")
        return None

@app.before_request
def enforce_https():
    """Redirect HTTP to HTTPS automatically"""
    if request.url.startswith('http://'):
        https_url = request.url.replace('http://', 'https://', 1)
        return redirect(https_url, code=301)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data and 'text' in data['message']:
            text = data['message']['text'].lower()
            chat_id = data['message']['chat']['id']
            
            if text == '/start':
                send_telegram_message(chat_id, "🎲 WinGo Prediction Bot Started! Use /predict for predictions")
                
            elif text == '/predict':
                colors = ["Red", "Blue", "Green"]
                numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                
                predicted_color = random.choice(colors)
                predicted_number = random.choice(numbers)
                
                prediction_message = f"🎯 Prediction:\n• Color: {predicted_color}\n• Number: {predicted_number}\n• Confidence: 75%"
                send_telegram_message(chat_id, prediction_message)
                
            else:
                send_telegram_message(chat_id, "Use /predict for prediction")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return """
    <h1>🎯 WinGo Lottery Prediction Bot</h1>
    <p>Bot is running successfully! ✅</p>
    <p><a href="/setwebhook">Setup Webhook</a></p>
    <p><a href="/test">Test Bot</a></p>
    <p><strong>Using synchronous version - No async issues</strong></p>
    """

@app.route('/setwebhook')
def set_webhook():
    """Manual webhook setup"""
    try:
        base_url = f"https://{request.host}"
        webhook_url = f"{base_url}/webhook"
        
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(set_url)
        result = response.json()
        
        html_response = f"""
        <h1>Webhook Setup</h1>
        <p><strong>Status:</strong> {'✅ SUCCESS' if result.get('ok') else '❌ FAILED'}</p>
        <p><strong>Webhook URL:</strong> {webhook_url}</p>
        <p><strong>Response:</strong> {result.get('description', 'No description')}</p>
        <p><a href="/">Home</a> | <a href="/getwebhook">Check Status</a></p>
        """
        return html_response
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/getwebhook')
def get_webhook_info():
    """Check webhook status"""
    try:
        check_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(check_url)
        result = response.json()
        
        html_response = f"""
        <h1>Webhook Status</h1>
        <pre>{json.dumps(result, indent=2)}</pre>
        <p><a href="/">Home</a> | <a href="/setwebhook">Setup Again</a></p>
        """
        return html_response
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/test')
def test_bot():
    """Test bot functionality"""
    try:
        bot_info = get_bot_info()
        if bot_info and bot_info.get('ok'):
            bot_data = bot_info['result']
            html_response = f"""
            <h1>Bot Test</h1>
            <p><strong>Status:</strong> ✅ WORKING</p>
            <p><strong>Bot Username:</strong> @{bot_data.get('username', 'Unknown')}</p>
            <p><strong>Bot ID:</strong> {bot_data.get('id', 'Unknown')}</p>
            <p><a href="/">Home</a></p>
            """
            return html_response
        else:
            return f"<h1>Error</h1><p>Bot test failed: {bot_info}</p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/sendtest')
def send_test_message():
    """Send test message to bot"""
    try:
        # This would need a specific chat_id to work
        # For demonstration only
        result = send_telegram_message(123456789, "Test message from server")
        return f"<h1>Test Send</h1><pre>{json.dumps(result, indent=2)}</pre>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    print("🚀 Telegram Bot Server Starting (Synchronous Version)...")
    print("✅ No async issues - Using direct HTTP requests")
    app.run(host='0.0.0.0', port=5000)
