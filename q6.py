from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

R, C = 4, 4
agent = (0,0)
pits = set()
wumpus = (0,0)

visited = set()
KB = []

steps = 0
score = 0
game_over = False
win = False


def init_world(rows, cols):
    global R, C, agent, pits, wumpus, visited, KB, steps, score, game_over, win

    R, C = rows, cols
    pits = set()
    visited = set()
    KB = []

    steps = 0
    score = 0
    game_over = False
    win = False

    for i in range(R):
        for j in range(C):
            if random.random() < 0.2 and (i,j) != (0,0):
                pits.add((i,j))

    wumpus = (random.randint(0,R-1), random.randint(0,C-1))

    agent = (0,0)
    visited.add((0,0))


def get_percepts(x,y):
    breeze, stench = False, False

    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx,ny = x+dx, y+dy
        if (nx,ny) in pits:
            breeze = True
        if (nx,ny) == wumpus:
            stench = True

    return breeze, stench


def tell(breeze, stench, x, y):
    cell = f"{x},{y}"

    if breeze: KB.append(f"B({cell})")
    else: KB.append(f"¬B({cell})")

    if stench: KB.append(f"S({cell})")
    else: KB.append(f"¬S({cell})")


def resolve(cell):
    if f"B({cell})" in KB and f"¬B({cell})" in KB:
        return False
    if f"S({cell})" in KB and f"¬S({cell})" in KB:
        return False
    return True


def ask_safe(x,y):
    global steps
    steps += 1
    return resolve(f"{x},{y}")


def neighbors(x,y):
    res = []
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx,ny = x+dx, y+dy
        if 0 <= nx < R and 0 <= ny < C:
            res.append((nx,ny))
    return res


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/init", methods=["POST"])
def init():
    data = request.json
    init_world(int(data["rows"]), int(data["cols"]))

    return jsonify({
        "agent": agent,
        "pits": list(pits),
        "wumpus": wumpus,
        "visited": list(visited),
        "safe_cells": list(visited),
        "kb": KB,
        "steps": steps,
        "score": score,
        "game_over": game_over,
        "win": win,
        "percepts": {"breeze": False, "stench": False}
    })


@app.route("/step", methods=["POST"])
def step():
    global agent, score, game_over, win

    if game_over:
        return jsonify({
            "agent": agent,
            "pits": list(pits),
            "wumpus": wumpus,
            "visited": list(visited),
            "safe_cells": list(visited),
            "kb": KB,
            "steps": steps,
            "score": score,
            "game_over": game_over,
            "win": win,
            "percepts": {"breeze": False, "stench": False}
        })

    x,y = agent
    breeze, stench = get_percepts(x,y)

    tell(breeze, stench, x, y)

    moves = neighbors(x,y)

    safe_moves = []
    for m in moves:
        if ask_safe(m[0], m[1]):
            safe_moves.append(m)

    agent = random.choice(safe_moves if safe_moves else moves)

    visited.add(agent)

    score += 10
    if breeze or stench:
        score -= 5

    if agent in pits or agent == wumpus:
        game_over = True
        win = False
        score -= 50

    if agent == (R-1, C-1):
        game_over = True
        win = True
        score += 100

    return jsonify({
        "agent": agent,
        "pits": list(pits),
        "wumpus": wumpus,
        "visited": list(visited),
        "safe_cells": list(visited),
        "kb": KB,
        "steps": steps,
        "score": score,
        "game_over": game_over,
        "win": win,
        "percepts": {"breeze": breeze, "stench": stench}
    })


if __name__ == "__main__":
    app.run(debug=True)