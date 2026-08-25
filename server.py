from flask import Flask, request, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}


@socketio.on("connect")
def connect():
    print("Connected:", request.sid)


@socketio.on("join")
def join(data):
    room = data["room"]

    if room not in rooms:
        rooms[room] = {
            "players": [],
            "choices": {}
        }

    if len(rooms[room]["players"]) >= 2:
        emit("room_full")
        return

    join_room(room)

    rooms[room]["players"].append(request.sid)

    emit("joined", {
        "player": len(rooms[room]["players"])
    })

    socketio.emit(
        "player_count",
        len(rooms[room]["players"]),
        room=room
    )

    if len(rooms[room]["players"]) == 2:
        socketio.emit("game_start", room=room)

    print(rooms)


@socketio.on("choice")
def choice(data):
    room = data["room"]
    player_choice = data["choice"]

    if room not in rooms:
        return

    rooms[room]["choices"][request.sid] = player_choice

    if len(rooms[room]["choices"]) == 2:
        p1, p2 = rooms[room]["players"]

        c1 = rooms[room]["choices"][p1]
        c2 = rooms[room]["choices"][p2]

        if c1 == c2:
            winner = "draw"
        elif (
            (c1 == "rock" and c2 == "scissors")
            or (c1 == "paper" and c2 == "rock")
            or (c1 == "scissors" and c2 == "paper")
        ):
            winner = p1
        else:
            winner = p2

        for player_sid, own_choice, opponent_choice in (
            (p1, c1, c2),
            (p2, c2, c1),
        ):
            if winner == "draw":
                personal_result = "draw"
            elif winner == player_sid:
                personal_result = "win"
            else:
                personal_result = "lose"

            socketio.emit(
                "round_result",
                {
                    "result": personal_result,
                    "my_choice": own_choice,
                    "enemy_choice": opponent_choice,
                },
                room=player_sid,
            )

        rooms[room]["choices"] = {}


@socketio.on("disconnect")
def disconnect():
    print("Disconnected:", request.sid)

    for room in list(rooms.keys()):
        if request.sid in rooms[room]["players"]:
            rooms[room]["players"].remove(request.sid)

            if request.sid in rooms[room]["choices"]:
                del rooms[room]["choices"][request.sid]

            socketio.emit("player_left", room=room)

            if len(rooms[room]["players"]) == 0:
                del rooms[room]
print("Сервер запущено на http://localhost:5000")
socketio.run(app, host="0.0.0.0", port=5000)