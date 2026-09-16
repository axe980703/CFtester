import json, os, socket, subprocess, sys, threading, time
from http.server import BasedHTTPRequestHandler, HTTPServer

PORT = 8765
HOST = "127.0.0.1"
MAX_UPTIME = 2 * 60 * 60



class GrabHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        
        try:
            data = json.loads(body)
            save_samples(data)

        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        
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


def _self_shutdown_timer(server):
    time.sleep(MAX_UPTIME)
    server.shutdown()


def run():
    server = HTTPServer((HOST, PORT), GrabHandler)
    threading.Thread(target=_self_shutdown_timer, args=(server,), daemon=True).start()
    server.serve_forever()

if __name__ == "__main__":
    run()

