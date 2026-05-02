import json
import socket
import threading

HOST = "0.0.0.0"
PORT = 6000

LARGURA_CAIXA = 42


class EspacoDeTuplas:
    def __init__(self):
        self.tuplas: list = []
        self._lock = threading.Lock()
        self._nova_tupla = threading.Condition(self._lock)

    def out(self, tupla: list) -> None:
        with self._nova_tupla:
            self.tuplas.append(tupla)
            self._nova_tupla.notify_all()
            self._imprimir_estado(f"OUT {tupla}")

    def in_(self, padrao: list) -> list:
        with self._nova_tupla:
            while True:
                for i, t in enumerate(self.tuplas):
                    if _casa(padrao, t):
                        del self.tuplas[i]
                        self._imprimir_estado(f"IN  {t}")
                        return t
                self._nova_tupla.wait()

    def rd(self, padrao: list) -> list:
        with self._nova_tupla:
            while True:
                for t in self.tuplas:
                    if _casa(padrao, t):
                        return t
                self._nova_tupla.wait()

    def _imprimir_estado(self, operacao: str) -> None:
        borda = "═" * LARGURA_CAIXA
        print(f"╔{borda}╗", flush=True)
        print(f"║  [{operacao}]".ljust(LARGURA_CAIXA + 1) + "║", flush=True)
        print(f"╠{borda}╣", flush=True)
        if self.tuplas:
            for t in self.tuplas:
                linha = f"  {t}"
                print(f"║{linha.ljust(LARGURA_CAIXA)}║", flush=True)
        else:
            print(f"║  (espaço vazio)".ljust(LARGURA_CAIXA + 1) + "║", flush=True)
        print(f"╚{borda}╝", flush=True)


def _casa(padrao: list, tupla: list) -> bool:
    if len(padrao) != len(tupla):
        return False
    return all(p is None or p == t for p, t in zip(padrao, tupla))


def _tratar_cliente(conn: socket.socket, addr, espaco: EspacoDeTuplas) -> None:
    with conn:
        buf = ""
        while True:
            dados = conn.recv(4096)
            if not dados:
                break
            buf += dados.decode()
            while "\n" in buf:
                linha, buf = buf.split("\n", 1)
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    msg = json.loads(linha)
                    op = msg.get("op", "").lower()
                    if op == "out":
                        espaco.out(msg["tupla"])
                        resposta = {"ok": True}
                    elif op == "in":
                        tupla = espaco.in_(msg["padrao"])
                        resposta = {"ok": True, "tupla": tupla}
                    elif op == "rd":
                        tupla = espaco.rd(msg["padrao"])
                        resposta = {"ok": True, "tupla": tupla}
                    else:
                        resposta = {"ok": False, "erro": f"operação desconhecida: {op}"}
                    conn.sendall((json.dumps(resposta) + "\n").encode())
                except Exception as e:
                    conn.sendall((json.dumps({"ok": False, "erro": str(e)}) + "\n").encode())


def main() -> None:
    espaco = EspacoDeTuplas()
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen()
    print(f"[ESPAÇO] Escutando em {HOST}:{PORT} ...", flush=True)
    while True:
        conn, addr = srv.accept()
        t = threading.Thread(target=_tratar_cliente, args=(conn, addr, espaco), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
