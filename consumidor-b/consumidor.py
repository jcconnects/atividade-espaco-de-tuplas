import json
import os
import socket
import time

ESPACO_HOST = "espaco"
ESPACO_PORT = 6000
NOME = os.environ.get("NOME_CONSUMIDOR", "CONSUMIDOR")


def conectar() -> socket.socket:
    for tentativa in range(10):
        try:
            conn = socket.create_connection((ESPACO_HOST, ESPACO_PORT))
            return conn
        except OSError:
            print(f"[{NOME}] Aguardando espaço... ({tentativa + 1}/10)", flush=True)
            time.sleep(1)
    raise RuntimeError("Não foi possível conectar ao espaço de tuplas.")


def in_(conn: socket.socket, padrao: list) -> list:
    msg = json.dumps({"op": "in", "padrao": padrao}) + "\n"
    conn.sendall(msg.encode())
    buf = ""
    while "\n" not in buf:
        buf += conn.recv(4096).decode()
    resposta = json.loads(buf.strip())
    if not resposta.get("ok"):
        raise RuntimeError(f"Erro ao buscar tupla: {resposta}")
    return resposta["tupla"]


def out(conn: socket.socket, tupla: list) -> None:
    msg = json.dumps({"op": "out", "tupla": tupla}) + "\n"
    conn.sendall(msg.encode())
    conn.recv(4096)


def main() -> None:
    conn = conectar()
    print(f"[{NOME}] Conectado ao espaço de tuplas. Aguardando tarefas...", flush=True)
    while True:
        tupla = in_(conn, ["tarefa", "processar", None])
        print(f"[{NOME}] IN obteve: {tupla}", flush=True)
        time.sleep(0.5)
        resultado = ["resultado", "ok", tupla[2]]
        out(conn, resultado)
        print(f"[{NOME}] OUT resultado: {resultado}", flush=True)


if __name__ == "__main__":
    main()
