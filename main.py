from flask import Flask, request, jsonify
import bot  # Import your main script

app = Flask(__name__)

@app.route('/')
def index():
    # Call your script function and return the result
    result = bot.main()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)