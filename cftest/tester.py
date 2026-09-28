import os, subprocess, time
from cftest import server


solution_path = "/home/kurban/CompeteCode/main"


def test_solution():
    smpl_dir = server.get_samples_dir()
    smpl_n = len(os.listdir(smpl_dir)) // 2
    
    for i in range(1, smpl_n + 1):
        if smpl_n > 1:
            print(f"TEST SAMPLE #{i}")
        test_sample(i)


def test_sample(smpl_n):
    smpl_dir = server.get_samples_dir() 
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


def main():
    server.ensure_server_running()
    
    if not server.wait_for_samples(timeout=7):
        print("Cannot grab samples, check if a codeforces tab is opened")
        return

    test_solution() 


if __name__ == "__main__":
    main()
