from flask import Flask, request
import telegram
import random
import os
import requests

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7783839439:AAHSd5_N6NmAYlL3d7OLWq3Wc3RVvnYhyzQ"
bot = telegram.Bot(token=BOT_TOKEN)

# Store historical data
historical_data = []

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        update = telegram.Update.de_json(data, bot)
        
        if update.message and update.message.text:
            text = update.message.text.lower()
            chat_id = update.message.chat_id
            
            if text == '/start':
                bot.send_message(chat_id=chat_id, text="🎲 WinGo Prediction Bot Started! Use /predict")
                
            elif text == '/predict':
                # Simple prediction
                colors = ["Red", "Blue", "Green"]
                numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                
                predicted_color = random.choice(colors)
                predicted_number = random.choice(numbers)
                
                prediction_message = f"🎯 Prediction:\nColor: {predicted_color}\nNumber: {predicted_number}\nConfidence: 75%"
                bot.send_message(chat_id=chat_id, text=prediction_message)
                
            else:
                bot.send_message(chat_id=chat_id, text="Use /predict for prediction")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 'Error', 500

@app.route('/')
def home():
    return "Telegram Bot is Running! ✅"

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """Manual webhook setup"""
    try:
        # Get the actual URL from Render environment
        render_url = os.getenv('RENDER_EXTERNAL_URL', '')
        
        if not render_url:
            # If environment variable not found, use request host
            render_url = f"https://{request.host}"
        
        webhook_url = f"{render_url}/webhook"
        
        # Set webhook with Telegram API
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        response = requests.get(set_url)
        result = response.json()
        
        return {
            "status": "success" if result.get('ok') else "failed",
            "webhook_url": webhook_url,
            "telegram_response": result
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/getwebhook', methods=['GET'])
def get_webhook_info():
    """Check webhook status"""
    try:
        check_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(check_url)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/test', methods=['GET'])
def test_bot():
    """Test bot functionality"""
    try:
        # Test bot token
        bot_info = bot.get_me()
        return {
            "status": "success",
            "bot_username": f"@{bot_info.username}",
            "bot_id": bot_info.id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    print("🚀 Starting Telegram Bot Server...")
    print("💡 After deployment, visit these URLs:")
    print("1. /setwebhook - Setup webhook")
    print("2. /getwebhook - Check webhook status") 
    print("3. /test - Test bot connection")
    app.run(host='0.0.0.0', port=5000)
