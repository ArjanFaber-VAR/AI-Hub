from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>⚡ F3 Engineering Control Center</title>

<style>
* {
    box-sizing: border-box;
    font-family: 'Segoe UI', sans-serif;
}

body {
    margin: 0;
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.header {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.title { font-size: 18px; font-weight: 600; }

.controls { display: flex; gap: 10px; }

button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border: none;
    padding: 9px 14px;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    font-size: 13px;
    transition: 0.2s;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(59,130,246,0.4);
}

button.secondary {
    background: linear-gradient(135deg, #64748b, #475569);
}

.container {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 12px;
    padding: 12px;
}

.panel {
    background: rgba(30, 41, 59, 0.6);
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
    display: flex;
    flex-direction: column;
}

.panel-header {
    padding: 8px 12px;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,0.3);
}

.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-ok { background: #22c55e; }
.status-down { background: #ef4444; }
.status-loading { background: #eab308; }

.panel-title {
    display: flex;
    align-items: center;
}

iframe {
    flex: 1;
    border: none;
    background: white;
}

.status {
    position: fixed;
    bottom: 15px;
    right: 15px;
    background: #22c55e;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 13px;
    opacity: 0;
    transform: translateY(10px);
    transition: 0.3s;
}

.status.show {
    opacity: 1;
    transform: translateY(0);
}
</style>
</head>

<body>

<div class="header">
    <div class="title">⚡ F3 Control Center</div>
    <div class="controls">
        <button onclick="ping()">Ping Backend</button>
        <button class="secondary" onclick="reloadAll()">Reload All</button>
    </div>
</div>

<div class="container">

    <!-- TECH -->
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">
                <div id="dot-8083" class="status-dot status-loading"></div>
                Technical Regulations
            </div>
        </div>
        <iframe id="frame-8083" src="https://vartechregulationsf3.ngrok.app"></iframe>
    </div>

    <!-- CHAT -->
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">
                <div id="dot-8084" class="status-dot status-loading"></div>
                Sporting Regulations
            </div>
        </div>
        <iframe id="frame-8084" src="https://sportingregulationsf3var.ngrok.app"></iframe>
    </div>

    <!-- TOOLS -->
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">
                <div id="dot-8085" class="status-dot status-loading"></div>
                General Questions
            </div>
        </div>
        <iframe id="frame-8085" src="https://YOUR-TOOLS-NGROK.app"></iframe>
    </div>

</div>

<div id="status" class="status"></div>

<script>

const agents = [
    { port: 8083, url: "https://vartechregulationsf3.ngrok.app" },
    { port: 8084, url: "https://sportingregulationsf3var.ngrok.app" },
    { port: 8085, url: "https://YOUR-TOOLS-NGROK.app" }
];

function showStatus(msg, color="#22c55e") {
    const el = document.getElementById("status");
    el.innerText = msg;
    el.style.background = color;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2500);
}

function ping() {
    fetch('/ping')
        .then(r => r.json())
        .then(d => showStatus(d.status))
        .catch(() => showStatus("Backend unreachable", "#ef4444"));
}

function reloadAll() {
    agents.forEach(a => {
        document.getElementById("frame-" + a.port).contentWindow.location.reload();
    });
    showStatus("Reloaded all dashboards");
}

function checkHealth() {
    agents.forEach(agent => {
        const dot = document.getElementById("dot-" + agent.port);
        dot.className = "status-dot status-loading";

        fetch(agent.url, { mode: "no-cors" })
            .then(() => {
                dot.className = "status-dot status-ok";
            })
            .catch(() => {
                dot.className = "status-dot status-down";
            });
    });
}

setInterval(checkHealth, 5000);
checkHealth();

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ping")
def ping():
    return jsonify({"status": "OK - Control Center Running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)