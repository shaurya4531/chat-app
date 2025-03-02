from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://shauryamule2020:pass%40321@cluster0.jk18o.mongodb.net/chatDB?retryWrites=true&w=majority"
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
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
