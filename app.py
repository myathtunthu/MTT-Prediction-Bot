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
        # Get Render URL automatically (for Render environment)
        render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-bot-name.onrender.com')
        webhook_url = f"{render_url}/webhook"
        
        # Set webhook
        set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(set_webhook_url)
        
        print(f"Webhook setup attempted: {webhook_url}")
        print(f"Telegram response: {response.json()}")
        
        return response.json().get('ok', False)
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
            {'draw_id': '1001', 'color': 'Red', 'number': 5, 'timestamp': '2024-01-15 14:30:00'},
            {'draw_id': '1002', 'color': 'Blue', 'number': 2, 'timestamp': '2024-01-15 15:30:00'},
            {'draw_id': '1003', 'color': 'Green', 'number': 8, 'timestamp': '2024-01-15 16:30:00'},
            {'draw_id': '1004', 'color': 'Red', 'number': 3, 'timestamp': '2024-01-15 17:30:00'},
            {'draw_id': '1005', 'color': 'Blue', 'number': 7, 'timestamp': '2024-01-15 18:30:00'}
        ]
        
        historical_data = mock_data
        print(f"Loaded {len(historical_data)} historical records")
        return True
        
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(), bot)
        
        if update.message and update.message.text:
            text = update.message.text.lower()
            chat_id = update.message.chat_id
            
            if text == '/start':
                response_text = "Hi! I am your lottery prediction bot. Use /predict for predictions."
                bot.send_message(chat_id=chat_id, text=response_text)
                
            elif text == '/predict':
                if not historical_data:
                    scrape_historical_data()
                
                color, number, confidence = predict_based_on_history()
                
                prediction_message = (
                    f"🎯 **Prediction** 🎯\n"
                    f"• Color: {color}\n"
                    f"• Number: {number}\n"
                    f"• Confidence: {confidence}%\n"
                    f"• Data: {len(historical_data)} records"
                )
                
                bot.send_message(chat_id=chat_id, text=prediction_message, parse_mode='Markdown')
                
            else:
                bot.send_message(chat_id=chat_id, text="Use /predict for prediction")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return "Telegram Bot is running! Webhook should be auto-configured."

@app.route('/setwebhook')
def manual_webhook_setup():
    """Manual webhook setup route"""
    success = setup_webhook()
    return f"Webhook setup {'successful' if success else 'failed'}"

# Initialize on server start
@app.before_first_request
def initialize():
    print("Initializing bot...")
    scrape_historical_data()
    setup_webhook()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
