import hashlib
import os
import random
import socket
import ssl
import string
import time

# — Personal details
# ————————————————————————

NAME      = "venkateshwara D"
MAILNUM   = "1"
MAIL1     = "venkateshdoijode1@gmail.com"
SKYPE     = "N/A"
BIRTHDATE = "30.04.1994"
COUNTRY   = "India"
ADDRNUM   = "2"
ADDRLINE1 = "123 Main Street"
ADDRLINE2 = "Villivakkam, Chennai, Tamil Nadu, India 600069"

INFO = {
    "NAME"      : NAME,
    "MAILNUM"   : MAILNUM,
    "MAIL1"     : MAIL1,
    "SKYPE"     : SKYPE,
    "BIRTHDATE" : BIRTHDATE,
    "COUNTRY"   : COUNTRY,
    "ADDRNUM"   : ADDRNUM,
    "ADDRLINE1" : ADDRLINE1,
    "ADDRLINE2" : ADDRLINE2,
}

# — Server config
# ————————————————————————

SERVER_HOST  = "18.202.148.130"
SERVER_PORTS = [3336, 8083, 8446, 49155, 3481, 65532]
CERT_DIR     = os.path.join(os.path.dirname(__file__), "certs")
KEY_FILE     = os.path.join(CERT_DIR, "client.key")
CERT_FILE    = os.path.join(CERT_DIR, "client.crt")

# — Helpers
# ————————————————————————

CHARS = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:',.<>?/`~"

def sha1(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def solve_pow(authdata, difficulty):
    target = "0" * difficulty
    print(f"  Solving POW difficulty {difficulty} ...", end="", flush=True)
    t0 = time.time()
    attempts = 0
    while True:
        suffix = "".join(random.choices(CHARS, k=random.randint(8, 16)))
        attempts += 1
        if sha1(authdata + suffix).startswith(target):
            elapsed = time.time() - t0
            print(f" done in {elapsed:.1f}s ({attempts:,} attempts)")
            print(f"  Suffix: {suffix!r}")
            return suffix

# — Main
# ————————————————————————

print("Connecting to server ...")

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE
try:
    ctx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
except ssl.SSLError as e:
    print(f"[ERROR] Could not load cert/key: {e}")
    raise SystemExit(1)

sock = None
for port in SERVER_PORTS:
    try:
        print(f"  Trying port {port} ...", end="", flush=True)
        raw  = socket.create_connection((SERVER_HOST, port), timeout=10)
        sock = ctx.wrap_socket(raw, server_hostname=SERVER_HOST)
        print(" connected!")
        break
    except Exception as e:
        print(f" failed: {e}")

if sock is None:
    print("All ports failed. Check your certs and network.")
    raise SystemExit(1)

authdata = ""

def read_line():
    buf = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            raise ConnectionError("Server closed connection")
        if ch == b"\n":
            return buf.decode("utf-8").strip()
        buf += ch

def send(msg):
    sock.sendall(msg.encode("utf-8"))

try:
    while True:
        line = read_line()
        if not line:
            continue
        print(f"<< {line}")
        parts = line.split(" ", 2)
        cmd   = parts[0]
        arg   = parts[1] if len(parts) > 1 else ""

        if cmd == "HELO":
            send("TOAKUEI\n")
            print(">> TOAKUEI")

        elif cmd == "POW":
            authdata   = arg
            difficulty = int(parts[2]) if len(parts) > 2 else 9
            suffix     = solve_pow(authdata, difficulty)
            send(suffix + "\n")
            print(f">> {suffix!r}")

        elif cmd == "END":
            send("OK\n")
            print(">> OK")
            print("\nApplication submitted successfully!")
            break

        elif cmd == "ERROR":
            print(f"Server error: {' '.join(parts[1:])}")
            break

        elif cmd in INFO:
            response = sha1(authdata + arg) + " " + INFO[cmd] + "\n"
            send(response)
            print(f">> {response.strip()}")

        else:
            if not authdata:
                print(f"  [WARN] No authdata yet, skipping command {cmd!r}")
                continue
            response = sha1(authdata + arg) + "\n"
            send(response)
            print(f"  [WARN] Unknown command {cmd!r}, sent empty response")

except (ConnectionError, OSError) as e:
    print(f"Connection lost: {e}")
finally:
    if sock:
        sock.close()