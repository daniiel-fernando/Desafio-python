import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import List, Optional

class Cliente:
    def __init__(self, endereco: str) -> None:
        self.endereco = endereco
        self.contas: List[Conta] = []

    def realizar_transacao(self, conta: 'Conta', transacao: 'Transacao') -> None:
        transacao.registrar(conta)

    def adicionar_conta(self, conta: 'Conta') -> None:
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, senha: str, endereco: str) -> None:
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.senha = senha

def log_transacao(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, bool) and result:
            print(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {func.__name__} realizada com sucesso!")
        return result
    return wrapper

class Conta:
    def __init__(self, numero: int, cliente: Cliente) -> None:
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int) -> 'Conta':
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def historico(self) -> 'Historico':
        return self._historico

    @log_transacao
    def sacar(self, valor: float) -> bool:
        if valor > self.saldo:
            print_message("Operação falhou! Você não tem saldo suficiente.")
        elif valor > 0:
            self._saldo -= valor
            print_message("Saque realizado com sucesso!", success=True)
            return True
        else:
            print_message("Operação falhou! O valor informado é inválido.")
        return False

    @log_transacao
    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self._saldo += valor
            print_message("Depósito realizado com sucesso!", success=True)
            return True
        else:
            print_message("Operação falhou! O valor informado é inválido.")
        return False

class ContaCorrente(Conta):
    def __init__(self, numero: int, cliente: Cliente, limite: float = 500, limite_saques: int = 3) -> None:
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor: float) -> bool:
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"])
        if valor > self._limite:
            print_message("Operação falhou! O valor do saque excede o limite.")
        elif numero_saques >= self._limite_saques:
            print_message("Operação falhou! Número máximo de saques excedido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self) -> str:
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self) -> None:
        self._transacoes: List[dict] = []

    @property
    def transacoes(self) -> List[dict]:
        return self._transacoes

    def adicionar_transacao(self, transacao: 'Transacao') -> None:
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> float:
        pass

    @abstractmethod
    def registrar(self, conta: Conta) -> None:
        pass

class Saque(Transacao):
    def __init__(self, valor: float) -> None:
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> None:
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor: float) -> None:
        self._valor = valor

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta: Conta) -> None:
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def print_message(message: str, success: bool = False) -> None:
    status = "===" if success else "@@@"
    print(f"\n{status} {message} {status}")

def menu() -> str:
    menu_text = """\n
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [7]\tSair
    => """
    return input(textwrap.dedent(menu_text))

def filtrar_cliente(cpf: str, clientes: List[Cliente]) -> Optional[Cliente]:
    return next((cliente for cliente in clientes if cliente.cpf == cpf), None)

def autenticar_cliente(cliente: Cliente) -> bool:
    senha = input("Informe a senha: ")
    if cliente.senha == senha:
        return True
    else:
        print_message("Senha incorreta!")
        return False

def recuperar_conta_cliente(cliente: Cliente) -> Optional[Conta]:
    if not cliente.contas:
        print_message("Cliente não possui conta!")
        return None

    print("\nEscolha uma das contas abaixo:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"[{i}] Conta Número: {conta.numero}, Saldo: R$ {conta.saldo:.2f}")

    while True:
        try:
            escolha = int(input("Digite o número da conta desejada: ")) - 1
            if 0 <= escolha < len(cliente.contas):
                return cliente.contas[escolha]
            else:
                print_message("Escolha inválida, tente novamente.")
        except ValueError:
            print_message("Entrada inválida, por favor insira um número.")

def depositar(clientes: List[Cliente]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print_message("Cliente não encontrado!")
        return

    if not autenticar_cliente(cliente):
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
    except ValueError:
        print_message("Valor inválido!")
        return

    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)

def sacar(clientes: List[Cliente]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print_message("Cliente não encontrado!")
        return

    if not autenticar_cliente(cliente):
        return

    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print_message("Valor inválido!")
        return

    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes: List[Cliente]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print_message("Cliente não encontrado!")
        return

    if not autenticar_cliente(cliente):
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = "\n".join([f"{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}" for transacao in transacoes]) or "Não foram realizadas movimentações."
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def criar_cliente(clientes: List[Cliente]) -> None:
    cpf = input("Informe o CPF (somente número): ")
    if filtrar_cliente(cpf, clientes):
        print_message("Já existe cliente com esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    senha = input("Crie uma senha: ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, senha=senha, endereco=endereco)
    clientes.append(cliente)
    print_message("Cliente criado com sucesso!", success=True)

def criar_conta(numero_conta: int, clientes: List[Cliente], contas: List[Conta]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print_message("Cliente não encontrado, fluxo de criação de conta encerrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print_message("Conta criada com sucesso!", success=True)

def listar_contas(contas: List[Conta]) -> None:
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

class IteradorContas:
    def __init__(self, contas: List[Conta]):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._contas):
            conta = self._contas[self._index]
            self._index += 1
            return {
                "numero": conta.numero,
                "saldo": conta.saldo,
                "agencia": conta.agencia,
                "titular": conta.cliente.nome
            }
        else:
            raise StopIteration

def main() -> None:
    clientes: List[Cliente] = []
    contas: List[Conta] = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)
        elif opcao == "2":
            sacar(clientes)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_cliente(clientes)
        elif opcao == "5":
            listar_contas(contas)
        elif opcao == "6":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "7":
            break
        else:
            print_message("Operação inválida, por favor selecione novamente a operação desejada.")

if __name__ == "__main__":
    main()
