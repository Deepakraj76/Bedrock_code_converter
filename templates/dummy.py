
# complex_input.py

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Mock database
users = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30}
]

@app.before_request
def log_request():
    print(f"{request.method} request for '{request.path}'")

@app.route('/api/users', methods=['GET'])
def get_all_users():
    return jsonify(users)

@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = next((u for u in users if u["id"] == id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def add_user():
    new_user = {
        "id": len(users) + 1,
        "name": request.json["name"],
        "age": request.json["age"]
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user_index = next((index for (index, u) in enumerate(users) if u["id"] == id), -1)
    if user_index != -1:
        users[user_index]["name"] = request.json.get("name", users[user_index]["name"])
        users[user_index]["age"] = request.json.get("age", users[user_index]["age"])
        return jsonify(users[user_index])
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user_index = next((index for (index, u) in enumerate(users) if u["id"] == id), -1)
    if user_index != -1:
        del users[user_index]
        return "", 204
    else:
        return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run(port=3002, debug=True)