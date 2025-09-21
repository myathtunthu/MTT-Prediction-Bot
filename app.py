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
        # Get Render URL automatically
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

def predict_based_on_history():
    """Make prediction based on historical data"""
    if not historical_data:
        return "Red", 5, 50
    
    # Simple prediction algorithm
    recent_data = historical_data[-5:] if len(historical_data) >= 5 else historical_data
    
    color_count = {}
    for data in recent_data:
        color = data['color']
        color_count[color] = color_count.get(color, 0) + 1
    
    predicted_color = min(color_count, key=color_count.get)
    
    recent_numbers = [data['number'] for data in recent_data]
    possible_numbers = [n for n in range(1, 11) if n not in recent_numbers]
    
    if possible_numbers:
        predicted_number = random.choice(possible_numbers)
    else:
        predicted_number = random.randint(1, 10)
    
    confidence = 60 + (len(historical_data) * 2)
    confidence = min(confidence, 85)
    
    return predicted_color, predicted_number, confidence

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telegram.Update.de_json(request.get_json(), bot)
        
        if update.message and update.message.text:
            text = update.message.text.lower()
            chat_id = update.message.chat_id
            
            if text == '/start':
                response_text = "Hi! I am your lottery prediction bot. Use /predict for predictions or /scrape to update data."
                bot.send_message(chat_id=chat_id, text=response_text)
                
            elif text == '/scrape':
                scrape_historical_data()
                bot.send_message(chat_id=chat_id, text=f"✅ Scraped {len(historical_data)} historical records. Use /predict for prediction.")
                
            elif text == '/predict':
                if not historical_data:
                    scrape_historical_data()
                
                color, number, confidence = predict_based_on_history()
                
                prediction_message = (
                    f"🎯 **Prediction** 🎯\n"
                    f"• Color: {color}\n"
                    f"• Number: {number}\n"
                    f"• Confidence: {confidence}%\n"
                    f"• Historical data: {len(historical_data)} records"
                )
                
                bot.send_message(chat_id=chat_id, text=prediction_message, parse_mode='Markdown')
                
            elif text == '/history':
                if historical_data:
                    history_text = f"Last {min(5, len(historical_data))} results:\n"
                    for data in historical_data[-5:]:
                        history_text += f"• {data['color']} {data['number']} ({data['timestamp']})\n"
                    bot.send_message(chat_id=chat_id, text=history_text)
                else:
                    bot.send_message(chat_id=chat_id, text="No historical data. Use /scrape first.")
                
            else:
                bot.send_message(chat_id=chat_id, text="Commands: /predict, /scrape, /history")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return "Telegram Bot is running! Use /setwebhook to configure webhook."

@app.route('/setwebhook')
def manual_webhook_setup():
    """Manual webhook setup route"""
    success = setup_webhook()
    return f"Webhook setup {'successful' if success else 'failed'}"

@app.route('/init')
def initialize():
    """Manual initialization endpoint"""
    scrape_historical_data()
    webhook_success = setup_webhook()
    return f"Bot initialized! Scraped {len(historical_data)} records. Webhook: {'success' if webhook_success else 'failed'}"

# Remove the deprecated before_first_request and use manual initialization
# The /init endpoint can be called once after deployment

if __name__ == '__main__':
    # Initialize on app start
    print("Starting bot initialization...")
    scrape_historical_data()
    setup_webhook()
    print("Bot started successfully!")
    app.run(host='0.0.0.0', port=5000)
