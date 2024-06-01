class ContaCorrente:
    def __init__(self):
        self.saldo = 0
        self.limite = 500
        self.extrato = ""
        self.numero_saques = 0
        self.LIMITE_SAQUE = 3

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.extrato += f"Depósito: R$ {valor:.2f}\n"
        else:
            print("Operação falhou! O valor informado é inválido.")

    def sacar(self, valor):
        if valor > 0 and valor <= self.saldo and self.numero_saques < self.LIMITE_SAQUE:
            self.saldo -= valor
            self.extrato += f"Saque: R$ {valor:.2f}\n"
            self.numero_saques += 1
        else:
            print("Operação falhou! Verifique o valor ou limite de saques.")

    def exibir_extrato(self):
        print("Extrato:")
        print(self.extrato)
        print(f"Saldo atual: R$ {self.saldo:.2f}")

usuarios = {}

def criar_usuario():
    cpf = input("Informe o CPF (somente números): ").strip()
    if cpf in usuarios:
        print("Erro! Já existe um usuário com esse CPF.")
        return
    
    nome = input("Informe o nome completo: ").strip()
    senha = input("Informe a senha: ").strip()
    usuarios[cpf] = {"nome": nome, "senha": senha, "conta": ContaCorrente()}
    print("Usuário criado com sucesso!")

def autenticar_usuario():
    cpf = input("Informe o CPF: ").strip()
    senha = input("Informe a senha: ").strip()

    usuario = usuarios.get(cpf)
    if usuario and usuario["senha"] == senha:
        return usuario["conta"]
    else:
        print("CPF ou senha incorretos.")
        return None

def exibir_menu():
    print(
        """
        [1] Depositar
        [2] Sacar
        [3] Extrato
        [4] Sair
        """
    )

def opcoes_menu(conta):
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            valor = float(input("Informe o valor do depósito: "))
            conta.depositar(valor)

        elif opcao == "2":
            valor = float(input("Informe o valor do saque: "))
            conta.sacar(valor)

        elif opcao == "3":
            conta.exibir_extrato()

        elif opcao == "4":
            break

        else:
            print("Opção inválida! Tente novamente.")

def listar_contas():
    if not usuarios:
        print("Nenhuma conta encontrada.")
        return

    for cpf, dados in usuarios.items():
        print(f"Nome: {dados['nome']}")

def main():
    while True:
        print(
            """
            [1] Criar usuário
            [2] Login
            [3] Listar contas
            [4] Sair
            """
        )
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            criar_usuario()

        elif opcao == "2":
            conta = autenticar_usuario()
            if conta:
                opcoes_menu(conta)

        elif opcao == "3":
            listar_contas()

        elif opcao == "4":
            break

        else:
            print("Opção inválida! Tente novamente.")

main()
