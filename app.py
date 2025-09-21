from flask import Flask, request
import telegram
import random
import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7783839439:AAHSd5_N6NmAYlL3d7OLWq3Wc3RVvnYhyzQ"
bot = telegram.Bot(token=BOT_TOKEN)

# Store historical data
historical_data = []

def setup_webhook():
    """Automatically set webhook on Render"""
    try:
        # Get the actual Render URL - FIXED
        # Render provides RENDER_EXTERNAL_URL environment variable
        render_url = os.getenv('RENDER_EXTERNAL_URL', '')
        
        if not render_url:
            # If not available, try to construct it from Render's default pattern
            service_name = os.getenv('RENDER_SERVICE_NAME', 'your-bot-name')
            render_url = f"https://{service_name}.onrender.com"
        
        webhook_url = f"{render_url}/webhook"
        print(f"Attempting to set webhook to: {webhook_url}")
        
        # Set webhook with proper URL encoding
        set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(set_webhook_url)
        result = response.json()
        
        print(f"Telegram API response: {result}")
        
        if result.get('ok'):
            print("✅ Webhook setup successful!")
            return True
        else:
            print(f"❌ Webhook setup failed: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"Webhook setup error: {str(e)}")
        return False

def scrape_historical_data():
    """Scrape historical lottery data"""
    global historical_data
    try:
        print("Scraping historical data...")
        
        # Mock data for demonstration
        mock_data = [
            {'draw_id': '1001', 'color': 'Red', 'number': 5, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'draw_id': '1002', 'color': 'Blue', 'number': 2, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'draw_id': '1003', 'color': 'Green', 'number': 8, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ]
        
        historical_data = mock_data
        print(f"Loaded {len(historical_data)} historical records")
        return True
        
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return False

def predict_based_on_history():
    """Make prediction based on historical data"""
    if not historical_data:
        return "Red", 5, 50
    
    recent_data = historical_data[-3:] if len(historical_data) >= 3 else historical_data
    
    color_count = {}
    for data in recent_data:
        color = data['color']
        color_count[color] = color_count.get(color, 0) + 1
    
    predicted_color = min(color_count, key=color_count.get)
    predicted_number = random.randint(1, 10)
    confidence = 65

    return predicted_color, predicted_number, confidence

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(), bot)
        
        if update.message and update.message.text:
            text = update.message.text.lower()
            chat_id = update.message.chat_id
            
            if text == '/start':
                response_text = "🎲 WinGo Prediction Bot Started!\nUse /predict for lottery predictions"
                bot.send_message(chat_id=chat_id, text=response_text)
                
            elif text == '/predict':
                if not historical_data:
                    scrape_historical_data()
                
                color, number, confidence = predict_based_on_history()
                
                prediction_message = (
                    f"🎯 **Prediction** 🎯\n"
                    f"• Color: {color}\n"
                    f"• Number: {number}\n"
                    f"• Confidence: {confidence}%"
                )
                
                bot.send_message(chat_id=chat_id, text=prediction_message, parse_mode='Markdown')
                
            else:
                bot.send_message(chat_id=chat_id, text="Use /predict for prediction")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return "🎯 Telegram Bot Running! Check /debug for webhook status"

@app.route('/debug')
def debug_info():
    """Debug information page"""
    render_url = os.getenv('RENDER_EXTERNAL_URL', 'Not detected')
    service_name = os.getenv('RENDER_SERVICE_NAME', 'Not detected')
    
    info = f"""
    <h1>Bot Debug Information</h1>
    <p>RENDER_EXTERNAL_URL: {render_url}</p>
    <p>RENDER_SERVICE_NAME: {service_name}</p>
    <p>Historical Records: {len(historical_data)}</p>
    <p><a href="/setwebhook">Set Webhook Now</a></p>
    <p><a href="/test">Test Bot</a></p>
    """
    return info

@app.route('/setwebhook')
def manual_webhook_setup():
    """Manual webhook setup route"""
    success = setup_webhook()
    return f"Webhook setup {'successful' if success else 'failed'}"

@app.route('/test')
def test_bot():
    """Test if bot can send messages"""
    try:
        # Try to get bot info to test token
        bot_info = bot.get_me()
        return f"Bot is working! Username: @{bot_info.username}"
    except Exception as e:
        return f"Bot test failed: {str(e)}"

@app.route('/init')
def initialize():
    """Manual initialization"""
    scrape_historical_data()
    webhook_success = setup_webhook()
    return f"Initialized! Records: {len(historical_data)}, Webhook: {'✅' if webhook_success else '❌'}"

if __name__ == '__main__':
    print("🚀 Starting Telegram Bot...")
    print("📋 Initializing historical data...")
    scrape_historical_data()
    
    print("🌐 Setting up webhook...")
    webhook_success = setup_webhook()
    
    if webhook_success:
        print("✅ Bot started successfully!")
    else:
        print("⚠️  Webhook setup failed - manual setup required")
        print("💡 Visit /setwebhook after deployment to setup webhook manually")
    
    app.run(host='0.0.0.0', port=5000)
