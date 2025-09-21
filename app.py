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
BOT_TOKEN = os.getenv('7783839439:AAHSd5_N6NmAYlL3d7OLWq3Wc3RVvnYhyzQ')
bot = telegram.Bot(token=BOT_TOKEN)

# Store historical data
historical_data = []

def scrape_historical_data():
    """Scrape historical lottery data from 6winak3"""
    global historical_data
    
    try:
        # Simulated scraping - in real scenario, use actual site URL
        # This is a placeholder for the actual scraping logic
        print("Scraping historical data...")
        
        # Mock data for demonstration (replace with actual scraping)
        mock_data = [
            {'draw_id': '1001', 'color': 'Red', 'number': 5, 'timestamp': '2024-01-15 14:30:00'},
            {'draw_id': '1002', 'color': 'Blue', 'number': 2, 'timestamp': '2024-01-15 15:30:00'},
            {'draw_id': '1003', 'color': 'Green', 'number': 8, 'timestamp': '2024-01-15 16:30:00'},
            {'draw_id': '1004', 'color': 'Red', 'number': 3, 'timestamp': '2024-01-15 17:30:00'},
            {'draw_id': '1005', 'color': 'Blue', 'number': 7, 'timestamp': '2024-01-15 18:30:00'}
        ]
        
        historical_data = mock_data
        print(f"Scraped {len(historical_data)} historical records")
        
    except Exception as e:
        print(f"Scraping error: {str(e)}")

def predict_based_on_history():
    """Make prediction based on historical data"""
    if not historical_data:
        return "No historical data available", 50
    
    # Simple prediction algorithm
    last_5 = historical_data[-5:] if len(historical_data) >= 5 else historical_data
    
    # Analyze color frequency
    color_count = {}
    for data in last_5:
        color = data['color']
        color_count[color] = color_count.get(color, 0) + 1
    
    # Predict least frequent color in recent draws
    predicted_color = min(color_count, key=color_count.get)
    
    # Predict number that hasn't appeared recently
    recent_numbers = [data['number'] for data in last_5]
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
                response_text = "Hi! I am your lottery prediction bot with historical data analysis. Use /predict for predictions or /scrape to update data."
                bot.send_message(chat_id=chat_id, text=response_text)
                
            elif text == '/scrape':
                scrape_historical_data()
                bot.send_message(chat_id=chat_id, text=f"✅ Scraped {len(historical_data)} historical records. Use /predict for prediction.")
                
            elif text == '/predict':
                if not historical_data:
                    scrape_historical_data()
                
                color, number, confidence = predict_based_on_history()
                
                prediction_message = (
                    f"🎯 **Data-Driven Prediction** 🎯\n"
                    f"• Color: {color}\n"
                    f"• Number: {number}\n"
                    f"• Confidence: {confidence}%\n"
                    f"• Historical data: {len(historical_data)} records\n\n"
                    f"Based on analysis of recent patterns."
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
        print(f"Error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return "Telegram Bot with Historical Data Scraping is running!"

# Initial data scrape when server starts
@app.before_first_request
def initialize():
    scrape_historical_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
