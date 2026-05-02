import json
import socket
import time

ESPACO_HOST = "espaco"
ESPACO_PORT = 6000
INTERVALO = 3


def conectar() -> socket.socket:
    for tentativa in range(10):
        try:
            conn = socket.create_connection((ESPACO_HOST, ESPACO_PORT))
            return conn
        except OSError:
            print(f"[LEITOR] Aguardando espaço... ({tentativa + 1}/10)", flush=True)
            time.sleep(1)
    raise RuntimeError("Não foi possível conectar ao espaço de tuplas.")


def rd(conn: socket.socket, padrao: list) -> list:
    msg = json.dumps({"op": "rd", "padrao": padrao}) + "\n"
    conn.sendall(msg.encode())
    buf = ""
    while "\n" not in buf:
        buf += conn.recv(4096).decode()
    resposta = json.loads(buf.strip())
    if not resposta.get("ok"):
        raise RuntimeError(f"Erro ao ler tupla: {resposta}")
    return resposta["tupla"]


def main() -> None:
    conn = conectar()
    print("[LEITOR] Conectado ao espaço de tuplas. Aguardando resultados...", flush=True)
    while True:
        tupla = rd(conn, ["resultado", "ok", None])
        print(f"[LEITOR] RD (leitura sem remover): {tupla}", flush=True)
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
