import json, os, socket, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = 8765
HOST = "127.0.0.1"
MAX_UPTIME = 2 * 60 * 60



class GrabHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            inputs, outputs = data["inp"], data["out"]


        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        
        save_samples(inputs, outputs)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        pass


def save_samples(inputs, outputs):
    save_dir = get_samples_dir()
    os.makedirs(save_dir, exist_ok=True)
        
    for i, (inp, out) in enumerate(zip(inputs, outputs), start=1):
        inp_path = os.path.join(save_dir, f"sample{i}.in")
        out_path = os.path.join(save_dir, f"sample{i}.out") 
        with open(inp_path, "w") as inpf:
            inpf.write(inp)    
        with open(out_path, "w") as outf:
            outf.write(out)


def clear_samples():
    smp_dir = get_samples_dir()
    for file in os.listdir(smp_dir):
        f_path = os.path.join(smp_dir, file)
        os.remove(f_path)


def get_samples_dir():
    work_dir = os.path.dirname(os.path.abspath(__file__))
    smpl_dir = os.path.join(work_dir, "samples")
    return smpl_dir


def is_server_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.04)
        return s.connect_ex((HOST, PORT)) == 0


def ensure_server_running():
    if is_server_running():
        return
    
    subprocess.Popen(
        [sys.executable, "-m", "cftest.server"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    for _ in range(20):
        if is_server_running():
            break
        time.sleep(0.05)


def _self_shutdown_timer(server):
    time.sleep(MAX_UPTIME)
    server.shutdown()


def wait_for_samples(timeout=7):
    smp_dir = get_samples_dir()
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.isdir(smp_dir) and any(f.endswith(".in") for f in os.listdir(smp_dir)):
            return True
        time.sleep(0.05)
    return False


def run():
    clear_samples()
    server = HTTPServer((HOST, PORT), GrabHandler)
    threading.Thread(target=_self_shutdown_timer, args=(server,), daemon=True).start()
    server.serve_forever()

if __name__ == "__main__":
    run()

