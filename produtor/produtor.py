import json
import socket
import time

ESPACO_HOST = "espaco"
ESPACO_PORT = 6000

TAREFAS = [
    ["tarefa", "processar", 1],
    ["tarefa", "processar", 2],
    ["tarefa", "processar", 3],
    ["tarefa", "processar", 4],
    ["tarefa", "processar", 5],
]


def conectar() -> socket.socket:
    for tentativa in range(10):
        try:
            conn = socket.create_connection((ESPACO_HOST, ESPACO_PORT))
            return conn
        except OSError:
            print(f"[PRODUTOR] Aguardando espaço... ({tentativa + 1}/10)", flush=True)
            time.sleep(1)
    raise RuntimeError("Não foi possível conectar ao espaço de tuplas.")


def out(conn: socket.socket, tupla: list) -> None:
    msg = json.dumps({"op": "out", "tupla": tupla}) + "\n"
    conn.sendall(msg.encode())
    resposta = json.loads(conn.recv(4096).decode().strip())
    if not resposta.get("ok"):
        raise RuntimeError(f"Erro ao enviar tupla: {resposta}")


def main() -> None:
    conn = conectar()
    print("[PRODUTOR] Conectado ao espaço de tuplas.", flush=True)
    for tarefa in TAREFAS:
        out(conn, tarefa)
        print(f"[PRODUTOR] OUT: {tarefa}", flush=True)
        time.sleep(1)
    print("[PRODUTOR] Todas as tarefas publicadas. Encerrando.", flush=True)
    conn.close()


if __name__ == "__main__":
    main()
