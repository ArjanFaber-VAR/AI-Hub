from flask import Flask, Response

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Landing Page</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            display: flex;
            height: 100vh;
            align-items: center;
            justify-content: center;
        }

        .container {
            text-align: center;
        }

        h1 {
            margin-bottom: 30px;
        }

        button {
            display: block;
            width: 220px;
            margin: 10px auto;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background: #2563eb;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: 0.2s ease;
        }

        button:hover {
            background: #1d4ed8;
            transform: scale(1.03);
        }
    </style>

    <script>
        function go(url) {
            window.location.href = url;
        }
    </script>
</head>

<body>
    <div class="container">
        <h1>My Landing Page</h1>

        <button onclick="go('https://myappf2.ngrok.app')">Open F2</button>
        <button onclick="go('https://myvarf3agent.ngrok.app')">Open F3</button>
        <button onclick="go('https://varagentcalendartool.ngrok.app')">Open Calendar</button>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return Response(HTML, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4001, debug=True)