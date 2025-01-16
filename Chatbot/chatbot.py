import tkinter as tk
from tkinter import scrolledtext
import random
import json
from datetime import datetime
from textblob import TextBlob
from difflib import get_close_matches
import sqlite3

# Load responses from JSON file
def load_responses(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Initialize database connection
def init_database():
    conn = sqlite3.connect('university_info.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS info (
                        topic TEXT PRIMARY KEY,
                        details TEXT
                    )''')
    conn.commit()
    return conn

# Function to query the database
def query_database(topic):
    cursor = db_conn.cursor()
    cursor.execute("SELECT details FROM info WHERE topic = ?", (topic,))
    result = cursor.fetchone()
    return result[0] if result else None

# Function to get a random agent name
def get_agent_name():
    return random.choice(agents)

# Function to save chat logs to a file
def save_chat_log(log_text):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open("chat_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} {log_text}\n")

# Function to handle sending messages
def send_message(input_text=None):
    global user_name, awaiting_feedback
    user_question = input_text if input_text else user_input.get()
    if not user_question.strip():
        return  # Ignore empty inputs

    timestamp = datetime.now().strftime("[%H:%M:%S]")
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"{timestamp} You: {user_question}\n", "user")
    save_chat_log(f"You: {user_question}")

    # Check for feedback if session is ending
    if awaiting_feedback:
        process_feedback(user_question)
        return

    # Check for exit condition
    if user_question.lower() in ["bye", "exit", "quit", "see you later", "goodbye"]:
        goodbye_message = f"{agent_name}: Thank you for chatting, {user_name}! Have a great day!\n"
        chat_window.insert(tk.END, f"{timestamp} {goodbye_message}\n", "agent")
        save_chat_log(goodbye_message.strip())
        request_feedback()
        return

    # Simulate random disconnection
    if random.random() < 0.05:  # 5% chance to disconnect
        disconnect_message = f"{agent_name}: Oops! It seems we've been disconnected. Please try again later."
        chat_window.insert(tk.END, f"{timestamp} {disconnect_message}\n", "agent")
        save_chat_log(disconnect_message.strip())
        chat_window.config(state=tk.DISABLED)
        root.after(2000, root.destroy)
        return

    # Get chatbot response
    response = get_response(user_question)
    chat_window.insert(tk.END, f"{timestamp} {agent_name}: {response}\n", "agent")
    save_chat_log(f"{agent_name}: {response}")
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    user_input.delete(0, tk.END)

# Function to get a response based on user input
def get_response(user_input):
    user_input_lower = user_input.lower()
    sentiment = TextBlob(user_input).sentiment.polarity

    # Check for database topics
    db_response = query_database(user_input_lower)
    if db_response:
        return db_response

    # Check for humor or small talk keywords
    if "joke" in user_input_lower:
        return random.choice(jokes)
    elif "hello" in user_input_lower or "hi" in user_input_lower:
        return f"Hello, {user_name}! How can I brighten your day?"

    # Check for exact matches
    if user_input_lower in responses:
        return responses[user_input_lower].format(name=user_name)

    # Check for close matches using difflib
    close_matches = get_close_matches(user_input_lower, responses.keys(), n=1, cutoff=0.8)
    if close_matches:
        closest_match = close_matches[0]
        return f"Did you mean '{closest_match}'? {responses[closest_match].format(name=user_name)}"

    # Sentiment-based fallback
    if sentiment > 0.5:
        return f"You seem really happy, {user_name}! Keep up the good vibes!"
    elif sentiment < -0.5:
        return f"I'm sorry to hear that, {user_name}. Maybe a campus counselor could help?"

    # General fallback response
    if fallback_responses:
        return random.choice(fallback_responses).format(name=user_name)
    else:
        return "I'm not sure how to respond to that, but I'll try to improve!"

# Function to clear chat history
def clear_chat():
    chat_window.config(state=tk.NORMAL)
    chat_window.delete(1.0, tk.END)
    chat_window.insert(tk.END, f"Chat reset! You're chatting with {agent_name}.\n", "agent")
    chat_window.config(state=tk.DISABLED)

# Function to reload responses dynamically
def reload_responses():
    global responses, fallback_responses, jokes
    try:
        data = load_responses('responses.json')
        responses = data['responses']
        fallback_responses = data.get('fallback_responses', [])
        jokes = data.get('jokes', [])
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, "Responses reloaded successfully.\n", "agent")
        chat_window.config(state=tk.DISABLED)
    except Exception as e:
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"Error reloading responses: {str(e)}\n", "agent")
        chat_window.config(state=tk.DISABLED)

# Function to set user name on startup
def set_user_name():
    global user_name
    user_name = name_input.get().strip()
    if user_name:
        name_popup.destroy()
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"Welcome to the University of Poppleton, {user_name}! You're chatting with {agent_name}.\n", "agent")
        chat_window.config(state=tk.DISABLED)

# Function to request feedback
def request_feedback():
    global awaiting_feedback
    awaiting_feedback = True
    feedback_message = f"{agent_name}: Was my assistance helpful today, {user_name}? Reply with Yes or No."
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    chat_window.insert(tk.END, f"{timestamp} {feedback_message}\n", "agent")
    save_chat_log(feedback_message.strip())
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)

# Function to process feedback
def process_feedback(user_response):
    global awaiting_feedback
    user_response_lower = user_response.strip().lower()
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    if user_response_lower in ["yes", "y"]:
        feedback_reply = f"{agent_name}: Thank you for your feedback, {user_name}! Have a wonderful day!"
    elif user_response_lower in ["no", "n"]:
        feedback_reply = f"{agent_name}: I'm sorry I couldn't be more helpful, {user_name}. I'll strive to do better next time."
    else:
        feedback_reply = f"{agent_name}: I didn't quite catch that, {user_name}. Please reply with Yes or No."
        chat_window.insert(tk.END, f"{timestamp} {feedback_reply}\n", "agent")
        save_chat_log(feedback_reply.strip())
        chat_window.config(state=tk.DISABLED)
        chat_window.see(tk.END)
        return

    chat_window.insert(tk.END, f"{timestamp} {feedback_reply}\n", "agent")
    save_chat_log(feedback_reply.strip())
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    awaiting_feedback = False
    root.after(2000, root.destroy)

# Initialize GUI
root = tk.Tk()
root.title("Chatbot")

# Custom fonts and colors
root.option_add("*Font", "Arial 12")
root.option_add("*Background", "#f5f5f5")
root.option_add("*Foreground", "#333333")
chat_window_color = "#ffffff"
chat_text_color = "#222222"
user_text_color = "#0056b3"
agent_text_color = "#2d862d"

# Create a scrolled text widget for chat history
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, height=20, width=60, bg=chat_window_color, fg=chat_text_color)
chat_window.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Tag styles for chat window
chat_window.tag_config("user", foreground=user_text_color, background="#e6f7ff", justify="right")
chat_window.tag_config("agent", foreground=agent_text_color, background="#f7ffe6", justify="left")

# Entry box for user input
user_input = tk.Entry(root, width=40)
user_input.grid(row=1, column=0, padx=10, pady=10)

# Buttons
send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=1, padx=10, pady=10)
clear_button = tk.Button(root, text="Clear Chat", command=clear_chat)
clear_button.grid(row=2, column=0, columnspan=3, pady=5)
reload_button = tk.Button(root, text="Reload Responses", command=reload_responses)
reload_button.grid(row=3, column=0, columnspan=3, pady=5)

# Adaptive buttons for common topics
common_topics = {
    "Admissions Info": "admissions",
    "Library Hours": "library",
    "Sports Facilities": "sports",
    "Scholarships": "scholarship",
    "Campus Events": "events",
    "Parking Info": "parking"
}

for idx, (label, keyword) in enumerate(common_topics.items()):
    topic_button = tk.Button(root, text=label, command=lambda k=keyword: send_message(k))
    topic_button.grid(row=4 + idx // 3, column=idx % 3, padx=5, pady=5)

# Load responses
data = load_responses('responses.json')
responses = data['responses']
fallback_responses = data.get('fallback_responses', [])
jokes = data.get('jokes', [
    "Why don't skeletons fight each other? They don't have the guts!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call fake spaghetti? An impasta!"
])

# Agent name
agents = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Jamie", "Riley", "Avery"]
agent_name = get_agent_name()

# Initialize database
db_conn = init_database()

# Initialize feedback tracking
awaiting_feedback = False

# Ask for user name
name_popup = tk.Toplevel(root)
name_popup.title("Welcome")
tk.Label(name_popup, text="Please enter your name:", font=("Arial", 12)).pack(pady=10)
name_input = tk.Entry(name_popup, width=30)
name_input.pack(pady=5)
tk.Button(name_popup, text="Start Chat", command=set_user_name).pack(pady=10)
name_popup.protocol("WM_DELETE_WINDOW", root.destroy)

# Start the main loop
root.mainloop()

# Close database connection when the application exits
db_conn.close()
