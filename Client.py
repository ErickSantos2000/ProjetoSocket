import socket

def run_cliente():
    carrinho = {} 
    total_carrinho = 0  

    try:
        # Configuração do socket do cliente
        socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip_servidor = "127.0.0.1"  # IP do servidor
        porta_servidor = 8000  # Porta do servidor
        socket_cliente.connect((ip_servidor, porta_servidor))

        menu = socket_cliente.recv(1024).decode()
        print("Menu de Opções:")
        print(menu)

        while True:
            compraClient = input("Informe o pruduto e a quantidade desejada, para ser adicionada ao carrinho de compra(Exemplo: ram, 3) / 'confirmar' para encerrar: ").upper()
            socket_cliente.send(compraClient.encode())

            if compraClient.lower() == "confirmar":
                break

            produto, quantidade = compraClient.split(',')
            quantidade = int(quantidade)
            carrinho[produto] = carrinho.get(produto, 0) + quantidade

            resposta = socket_cliente.recv(1024).decode()
            print(resposta)

        total_compra = socket_cliente.recv(1024).decode()
        if total_compra:
            print(total_compra)

            metodo_pagamento = input("Escolha o método de pagamento (PIX, BOLETO, CARTAO) ou digite 'terminar' para cancelar a compra: ").lower()
            socket_cliente.send(metodo_pagamento.encode())


            resposta_final = socket_cliente.recv(1024).decode()
            print(resposta_final)

            if carrinho:
                print("Seu carrinho de produtos:")
                for produto, quantidade in carrinho.items():
                    print(f"{quantidade}x {produto}")
                print(f"{total_compra}")

        socket_cliente.close()
        print("Conexão com o servidor fechada")

    except Exception as e:
        print("Ocorreu um erro:", e)

run_cliente()