from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Store the latest iot data in memory
latest_login_data:list[dict] = []
password='123456'
token = 'acustomgeneratedtokenforapi'

def is_authorized(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header:
        return False
    return auth_header == f"Bearer {token}"



# route for recieving iot data
@app.route('/webhook', methods=['POST'])
def home():
    # if not is_authorized(request):
    #     return "Unauthorized", 401
    data = request.json
    global latest_login_data
    password_sent = data['data']
    if password_sent == password:
        latest_login_data.append({
            'time': str(datetime.now()),
            'status': 'Correct Password',
        })
        return "Correct Password", 200
    else:
        latest_login_data.append({
            'time': str(datetime.now()),
            'status': 'Wrong Password',
        })
        return "Wrong Password", 200
    

@app.route('/data')
def data():
    data_str = []
    for dt in latest_login_data:
        key = dt['time']
        value= dt['status']
        data_str.append(f'Time: {key}\nStatus:{value}\n-----------------\n')
    result = ''.join(data_str)
    return {'data': result}

@app.route('/')
def display():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Home Security Log</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 0;
        }
        h3 {
            color: #555;
            font-weight: normal;
            margin-top: 5px;
        }
        #log-container {
            margin-top: 30px;
            padding: 15px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .entry {
            padding: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 4px;
        }
        .correct {
            border-color: #2ecc71;
            background-color: #e9f9ee;
            color: #2c662d;
        }
        .wrong {
            border-color: #e74c3c;
            background-color: #faeaea;
            color: #a94442;
        }
        .timestamp {
            font-size: 0.9em;
            color: #999;
        }
    </style>
</head>
<body>
    <h1>Home Security System</h1>
    <h3>Status log of your entry system</h3>
    <div id="log-container">Loading logs...</div>

    <script>
        async function fetchData() {
            try {
                const res = await fetch("/data");
                const json = await res.json();
                const rawData = json.data.trim().split('-----------------').filter(e => e.trim() !== '');
                const logContainer = document.getElementById("log-container");
                logContainer.innerHTML = "";

                rawData.forEach(entry => {
                    const lines = entry.trim().split("\\n");
                    const time = lines[0].replace("Time: ", "");
                    const status = lines[1].replace("Status:", "").trim();

                    const div = document.createElement("div");
                    div.classList.add("entry");
                    div.classList.add(status === "Correct Password" ? "correct" : "wrong");
                    div.innerHTML = `
                        <div><strong>${status}</strong></div>
                        <div class="timestamp">${time}</div>
                    `;
                    logContainer.prepend(div); // newest on top
                });
            } catch (err) {
                document.getElementById("log-container").innerText = "Error fetching data.";
            }
        }

        setInterval(fetchData, 3000);
        fetchData(); // Initial fetch
    </script>
</body>
</html>
    """)




if __name__ == '__main__':
    app.run(port=8000)
