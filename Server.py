import socket
import threading

produtos = {
    "CPU": 500,
    "GPU": 1600,
    "RAM": 200,
    "SSD": 300,
    "FANS": 50,
    "PENDRIVE": 30,
    "GABINETE": 350
}

total_receita = 0
receita_lock = threading.Lock()

def enviar_menu(socket_cliente):
    menu = "\n".join([f"{produto}: R${preco}" for produto, preco in produtos.items()])
    socket_cliente.send(menu.encode()) 

def adicionar_ao_carrinho(socket_cliente, carrinho):
    compra = socket_cliente.recv(1024).decode()
    if compra.lower() == "confirmar":
        return False

    produto, quant = compra.split(',')
    quant = int(quant)
    if produto in produtos:
        carrinho[produto] = carrinho.get(produto, 0) + quant
        preco_total = produtos[produto] * quant
        resposta = f"{quant}x {produto} foi inserido ao carrinho de compras. Valor total: R${preco_total}"
    else:
        resposta = "Produto não foi encontrado"
    socket_cliente.send(resposta.encode())
    return True

def calcular_total_e_enviar(socket_cliente, carrinho):
    total_compra = sum(produtos[produto] * quant for produto, quant in carrinho.items())
    socket_cliente.send(f"Valor do produto: R${total_compra}".encode())
    return total_compra

def escolher_metodo_pagamento(socket_cliente, total_compra):
    global total_receita 

    metodo_pagamento = socket_cliente.recv(1024).decode().lower()
    if metodo_pagamento in ["pix", "boleto", "cartao"]:
        with receita_lock:
            total_receita += total_compra
        socket_cliente.send(f"Você escolheu o método de pagamento: {metodo_pagamento}".encode())
        return True
    elif metodo_pagamento == 'terminar':
        socket_cliente.send("Cancelando compra.".encode())
        return False
    else:
        socket_cliente.send("Método de pagamento inválido. Cancelando compra.".encode())
        return False
def handle_client(socket_cliente, endereco_cliente):
    carrinho = {}

    try:
        enviar_menu(socket_cliente)

        while adicionar_ao_carrinho(socket_cliente, carrinho):
            pass

        print("Carrinho do Cliente:")
        for produto, quant in carrinho.items():
            preco_unidade = produtos[produto]
            preco_total_produto = preco_unidade * quant
            print(f"{quant}x {produto}: R${preco_total_produto}")

        total_compra = calcular_total_e_enviar(socket_cliente, carrinho)
        print(f"Valor do produto: R${total_compra}")

        if carrinho:
            if escolher_metodo_pagamento(socket_cliente, total_compra):
                print(f"Total acumulado de vendas(receita): R${total_receita}")

    except Exception as e:
        print("Ocorreu um erro:", e)

    socket_cliente.close()
    print(f"Conexão com o cliente {endereco_cliente[0]}:{endereco_cliente[1]} fechada")


def run_servidor():
    try:
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_servidor = "127.0.0.1"
        porta = 8000
        socket_servidor.bind((ip_servidor, porta))
        socket_servidor.listen(5)
        print(f"Ouvindo {ip_servidor}:{porta}")

        while True:
            socket_cliente, endereco_cliente = socket_servidor.accept()
            print(f"Conexão aceita de {endereco_cliente[0]}:{endereco_cliente[1]}")

            cliente_thread = threading.Thread(target=handle_client, args=(socket_cliente, endereco_cliente))
            cliente_thread.start()

    except Exception as e:
        print("Ocorreu um erro:", e)

    finally:
        socket_servidor.close()

run_servidor()