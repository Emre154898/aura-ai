from flask import Flask, request, jsonify
import tasks

app = Flask(__name__)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify([
        {"id": row[0], "task": row[1], "done": bool(row[2])}
        for row in tasks.list_tasks()
    ])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    task = data.get("task", "").strip()

    if not task:
        return jsonify({"error": "Görev boş olamaz"}), 400

    tasks.add(task)
    return jsonify({"ok": True})

@app.route("/tasks/<int:task_id>/done", methods=["POST"])
def done(task_id):
    tasks.complete(task_id)
    return jsonify({"ok": True})

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove(task_id):
    tasks.delete(task_id)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
