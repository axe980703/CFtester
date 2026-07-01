import urllib.request, json, os, subprocess, websocket


ffox = "http://127.0.0.1:9222/json"
jq = "(() => {let inp = Array.from(document.querySelectorAll('div.input pre')).map(x => x.innerText.trim());let out = Array.from(document.querySelectorAll('div.output pre')).map(x => x.innerText.trim());return JSON.stringify({inp, out});})()"
solution_path = os.path.expanduser("~/CompeteCode/main")


def get_tab_websocket():
    try:
        with urllib.request.urlopen(ffox, timeout=2) as resp:
            tabs = json.loads(resp.read().decode())
        
        for tab in tabs:
            url = tab.get("url", "")
            if "codeforces.com/contest" in url:
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


def get_samples_dir():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    smpl_dir = os.path.join(work_dir, "samples")
    return smpl_dir 


def save_samples(inputs, outputs):
    save_dir = get_samples_dir()
    os.makedirs(save_dir, exist_ok=True)

    for file in os.listdir(save_dir):
        f_path = os.path.join(save_dir, file)
        os.remove(f_path)
    
    for i, (inp, out) in enumerate(zip(inputs, outputs), start=1):
        inp_path = os.path.join(save_dir, f"sample{i}.in")
        out_path = os.path.join(save_dir, f"sample{i}.out") 
        with open(inp_path, "w") as inpf:
            inpf.write(inp)    
        with open(out_path, "w") as outf:
            outf.write(out)
 

def test_sample(smpl_n):
    smpl_dir = get_samples_dir() 
    inp_path = os.path.join(smpl_dir, f"sample{smpl_n}.in")
    out_path = os.path.join(smpl_dir, f"sample{smpl_n}.out")
    
    with open(inp_path) as inp_file:
        result = subprocess.run(
            [solution_path],
            stdin=inp_file,
            capture_output=True,
            text=True,
            timeout=4
        )    

    got_output = result.stdout
    with open(out_path, "r") as out_file:
        correct_output = out_file.read()
    
    check_outputs(got_output, correct_output)


def check_outputs(got_out, cor_out):
    got_rows, cor_rows = got_out.split("\n"), cor_out.split("\n")

    dif = abs(len(got_rows) - len(cor_rows))
    if len(got_rows) < len(cor_rows):
        got_rows += [""] * dif
    if len(cor_rows) < len(got_rows):
        cor_rows += [""] * dif

    for i, (got_row, cor_row) in enumerate(zip(got_rows, cor_rows), start=1):
        g_row, c_row = got_row.strip(), cor_row.strip()
        ok = (g_row == c_row)
        color = ["\033[91m", "\033[92m"][int(ok)]
        msg = ('' if ok else f'  (expected: "{c_row}")')
        print(color + g_row, msg)
    
    print("\033[0m")


def test_solution():
    smpl_dir = get_samples_dir()
    smpl_n = len(os.listdir(smpl_dir)) // 2
    
    for i in range(1, smpl_n + 1):
        if smpl_n > 1:
            print(f"TEST SAMPLE #{i}")
        test_sample(i)


socket_url = get_tab_websocket()

if socket_url:
    ws = websocket.create_connection(socket_url, suppress_origin=True)

    call(ws, "Page.enable", 1)
    call(ws, "Runtime.enable", 2) 

    response = call(ws, "Runtime.evaluate", 7, {"expression": jq, "returnByValue": True})
            
    ws.close()

    jsresp = json.loads(response["result"]["result"]["value"])
    inputs, outputs = jsresp["inp"], jsresp["out"]
    
    save_samples(inputs, outputs)
    test_solution() 
