import urllib.request, json
from websocket import create_connection


ffox = "http://127.0.0.1:9222/json"
jq = "(() => {let inp = Array.from(document.querySelectorAll('div.input pre')).map(x => x.innerText.trim());let out = Array.from(document.querySelectorAll('div.output pre')).map(x => x.innerText.trim());return JSON.stringify({inp, out});})()"


def get_tab_websocket():
    try:
        with urllib.request.urlopen(ffox, timeout=2) as resp:
            tabs = json.loads(resp.read().decode())
        
        for tab in tabs:
            url = tab.get("url", "")
            if "codeforces.com/contest/2211" in url:
                return tab["webSocketDebuggerUrl"]
        
        print("No opened Codeforces tabs")   
 
    except Exception as e:
        print("Could not connect to Firefox port 9222")

    return None


def call(ws, method, msg_id, params={}):
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == msg_id:
            return msg


def process_data(raw):
    raw = json.loads(raw)
    inp, out = raw["inp"], raw["out"]
    print(inp, out)   
    return 1, 2


socket_url = get_tab_websocket()

if socket_url:
    ws = create_connection(socket_url, suppress_origin=True)

    call(ws, "Page.enable", 1)
    call(ws, "Runtime.enable", 2) 

    response = call(ws, "Runtime.evaluate", 7, {"expression": jq, "returnByValue": True})
            
    ws.close()

    raw_res = response["result"]["result"]["value"]

    inputs, outputs = process_data(raw_res)
    


