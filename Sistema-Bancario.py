import sqlite3
from datetime import datetime
from typing import List, Optional
import textwrap
from abc import ABC, abstractmethod

# Conexão com o banco de dados SQLite
con = sqlite3.connect('banco.db')
cur = con.cursor()

# Funções para criação e manipulação do banco de dados
def criar_tabela_usuario():
    cur.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data_nascimento TEXT,
        cpf TEXT UNIQUE,
        senha TEXT,
        endereco TEXT,
        email TEXT,
        agencia TEXT,
        tipo_conta TEXT
    )
    ''')
    con.commit()

def inserir_usuario(nome, data_nascimento, cpf, senha, endereco, email, agencia, tipo_conta):
    cur.execute('''
    INSERT INTO usuarios (nome, data_nascimento, cpf, senha, endereco, email, agencia, tipo_conta)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, data_nascimento, cpf, senha, endereco, email, agencia, tipo_conta))
    con.commit()

def autenticar_usuario(cpf, senha):
    cur.execute('SELECT * FROM usuarios WHERE cpf = ? AND senha = ?', (cpf, senha))
    return cur.fetchone()

# Decorador de log atualizado
def log_transacao(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        log_entry = (
            f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - "
            f"Função: {func.__name__} - "
            f"Args: {args} - "
            f"Kwargs: {kwargs} - "
            f"Retorno: {result}\n"
        )
        with open("log.txt", "a") as log_file:
            log_file.write(log_entry)
        return result
    return wrapper

class Cliente:
    def __init__(self, endereco: str) -> None:
        self.endereco = endereco
        self.contas: List['Conta'] = []

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

def autenticar_cliente(cpf: str, senha: str, clientes: List[PessoaFisica]) -> Optional[PessoaFisica]:
    cliente = filtrar_cliente(cpf, clientes)
    if cliente and cliente.senha == senha:
        return cliente
    return None

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

def depositar(clientes: List[PessoaFisica]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    senha = input("Informe a senha do cliente: ")
    cliente = autenticar_cliente(cpf, senha, clientes)

    if not cliente:
        print_message("Cliente não encontrado ou senha incorreta!")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
    except ValueError:
        print_message("Valor inválido!")
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)

def sacar(clientes: List[PessoaFisica]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    senha = input("Informe a senha do cliente: ")
    cliente = autenticar_cliente(cpf, senha, clientes)

    if not cliente:
        print_message("Cliente não encontrado ou senha incorreta!")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print_message("Valor inválido!")
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes: List[PessoaFisica]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    senha = input("Informe a senha do cliente: ")
    cliente = autenticar_cliente(cpf, senha, clientes)

    if not cliente:
        print_message("Cliente não encontrado ou senha incorreta!")
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        print("\n=============== EXTRATO ===============")
        transacoes = conta.historico.transacoes
        if not transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for transacao in transacoes:
                print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        print(f"\nSaldo: R$ {conta.saldo:.2f}")
        print("========================================")

def criar_conta(clientes: List[PessoaFisica]) -> None:
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print_message("Cliente não encontrado!")
        return

    numero_conta = len(cliente.contas) + 1
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    cliente.adicionar_conta(conta)
    print_message("Conta criada com sucesso!", success=True)

def listar_contas(clientes: List[PessoaFisica]) -> None:
    if not clientes:
        print_message("Não há clientes cadastrados.")
        return

    for cliente in clientes:
        if cliente.contas:
            print(f"\nCliente: {cliente.nome}")
            for conta in cliente.contas:
                print(conta)
        else:
            print(f"\nCliente: {cliente.nome} não possui contas.")

def criar_cliente(clientes: List[PessoaFisica]) -> None:
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    cpf = input("Informe o CPF (somente números): ")
    senha = input("Informe uma senha: ")
    endereco = input("Informe o endereço: ")
    email = input("Informe o email: ")
    agencia = input("Informe a agência: ")
    tipo_conta = input("Informe o tipo de conta: ")

    inserir_usuario(nome, data_nascimento, cpf, senha, endereco, email, agencia, tipo_conta)
    cliente = PessoaFisica(nome, data_nascimento, cpf, senha, endereco)
    clientes.append(cliente)
    print_message("Cliente criado com sucesso!", success=True)

def main() -> None:
    clientes: List[PessoaFisica] = []

    criar_tabela_usuario()

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)
        elif opcao == "2":
            sacar(clientes)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_conta(clientes)
        elif opcao == "5":
            listar_contas(clientes)
        elif opcao == "6":
            criar_cliente(clientes)
        elif opcao == "7":
            break
        else:
            print_message("Operação inválida, por favor selecione novamente a operação desejada.")

if __name__ == "__main__":
    main()
