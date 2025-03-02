from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room
from pymongo import MongoClient
import os

# Get port from environment variable (default 8080 for Railway)
port = int(os.environ.get("PORT", 8080))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB Atlas Connection (Using Environment Variables for Security)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MongoDB URI is not set in environment variables!")

client = MongoClient(MONGO_URI)
db = client["chatDB"]
messages_collection = db["messages"]

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    message_data = {"username": data["username"], "message": data["msg"], "room": room}

    # Store message in MongoDB
    messages_collection.insert_one(message_data)

    # Broadcast message to all clients in the room
    send({"msg": f"{data['username']}: {data['msg']}"}, room=room)

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)

    # Fetch chat history from MongoDB
    chat_history = list(messages_collection.find({"room": room}, {"_id": 0}))

    for msg in chat_history:
        send({"msg": f"{msg['username']}: {msg['message']}"}, room=room)

    send({"msg": f"{data['username']} has joined the chat"}, room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
