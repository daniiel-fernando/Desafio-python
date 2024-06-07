# Sistema Bancário Simples em Python

Este é um projeto de sistema bancário simples desenvolvido em Python como parte de um desafio de programação. O sistema bancário inclui funcionalidades básicas como depósito, saque, exibição de extrato, criação de clientes e contas.

## Funcionalidades

O sistema bancário oferece as seguintes funcionalidades:

1. **Depósito**: Permite aos clientes fazer depósitos em suas contas.
2. **Saque**: Permite aos clientes fazer saques de suas contas, respeitando limites configurados.
3. **Extrato**: Permite aos clientes visualizar o extrato de suas contas.
4. **Nova Conta**: Permite a criação de uma nova conta para um cliente existente.
5. **Listar Contas**: Lista todas as contas criadas no sistema.
6. **Novo Usuário**: Permite a criação de um novo cliente.

## Estrutura do Projeto

O projeto está estruturado da seguinte forma:

- `banco.py`: Contém as classes principais do sistema bancário, como `Cliente`, `Conta`, `Transacao`, etc.
- `main.py`: Contém a lógica principal do programa, incluindo o menu interativo e a interação com o usuário.
- `test_banco.py`: Contém testes unitários para as classes e métodos principais do sistema bancário.

## Requisitos

O projeto requer Python 3.x para ser executado. Não são necessárias bibliotecas externas além das bibliotecas padrão do Python.

## Como Executar

Para executar o sistema bancário, basta executar o arquivo `main.py` com Python:

```bash
python main.py
