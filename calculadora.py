import tkinter as tk


def calcular(numero1, numero2, operacao):

    if operacao == "+":
        return (numero1 + numero2)

    elif operacao == "-":
        return(numero1 - numero2)

    elif operacao == "*":
        return(numero1 * numero2)

    elif operacao == "**":
        return(numero1 ** numero2)

    elif operacao == "/":
        if numero2 == 0:
            return("Não é possível dividir um número com 0")
        else:
            return(numero1 / numero2)

    else:
        return("Digite uma operação válida")


# variaveis que guardam o estado da calculadora
digitado = "0"        # o que aparece no visor
numero1 = None        # primeiro numero da conta
operacao = ""         # operação escolhida
novo_numero = True    # se for True, o próximo dígito vai começa um número novo


def mostrar():
    visor.config(text=digitado)


def formatar(numero):
    # 5.0 formata para "5", 2.5 continua "2.5"
    if numero == int(numero):
        return str(int(numero))
    return str(round(numero, 8))


def clicar_numero(digito):
    global digitado, novo_numero
    if novo_numero or digitado == "0":
        digitado = digito
    elif len(digitado) < 12:
        digitado = digitado + digito
    novo_numero = False
    mostrar()


def clicar_ponto():
    global digitado, novo_numero
    if novo_numero:
        digitado = "0."
        novo_numero = False
    elif "." not in digitado:
        digitado = digitado + "."
    mostrar()


def clicar_operacao(simbolo):
    global numero1, operacao, novo_numero
    if operacao != "" and novo_numero:
        # apertou duas operações seguidas faz a substituição
        operacao = simbolo
        return
    if operacao != "" and not novo_numero:
        # fecha contas pendentes
        if not igual():
            return
    numero1 = float(digitado)
    operacao = simbolo
    novo_numero = True


def igual():
    global digitado, numero1, operacao, novo_numero
    if operacao == "" or novo_numero:
        return True    # não tem conta pra fazer
    numero2 = float(digitado)
    resultado = calcular(numero1, numero2, operacao)
    numero1 = None
    operacao = ""
    novo_numero = True
    if type(resultado) == str:
        # a função calcular retornou mensagem de erro
        print(resultado)
        digitado = "0"
        visor.config(text="Erro")
        return False
    digitado = formatar(resultado)
    mostrar()
    return True


def limpar():
    global digitado, numero1, operacao, novo_numero
    digitado = "0"
    numero1 = None
    operacao = ""
    novo_numero = True
    mostrar()


# ---- janela ----
janela = tk.Tk()
janela.title("Calculadora")
janela.resizable(False, False)

visor = tk.Label(janela, text="0", anchor="e", font=("Arial", 24),
                 bg="white", width=14, padx=10, pady=10)
visor.grid(row=0, column=0, columnspan=4, padx=4, pady=4, sticky="nsew")


def criar_botao(texto, linha, coluna, comando, colunas=1, linhas=1):
    botao = tk.Button(janela, text=texto, font=("Arial", 16),
                      width=4, height=2, command=comando)
    botao.grid(row=linha, column=coluna, columnspan=colunas,
               rowspan=linhas, sticky="nsew", padx=2, pady=2)


criar_botao("C", 1, 0, limpar)
criar_botao("**", 1, 1, lambda: clicar_operacao("**"))
criar_botao("/", 1, 2, lambda: clicar_operacao("/"))
criar_botao("*", 1, 3, lambda: clicar_operacao("*"))

criar_botao("7", 2, 0, lambda: clicar_numero("7"))
criar_botao("8", 2, 1, lambda: clicar_numero("8"))
criar_botao("9", 2, 2, lambda: clicar_numero("9"))
criar_botao("-", 2, 3, lambda: clicar_operacao("-"))

criar_botao("4", 3, 0, lambda: clicar_numero("4"))
criar_botao("5", 3, 1, lambda: clicar_numero("5"))
criar_botao("6", 3, 2, lambda: clicar_numero("6"))
criar_botao("+", 3, 3, lambda: clicar_operacao("+"))

criar_botao("1", 4, 0, lambda: clicar_numero("1"))
criar_botao("2", 4, 1, lambda: clicar_numero("2"))
criar_botao("3", 4, 2, lambda: clicar_numero("3"))
criar_botao("=", 4, 3, igual, linhas=2)

criar_botao("0", 5, 0, lambda: clicar_numero("0"), colunas=2)
criar_botao(".", 5, 2, clicar_ponto)

janela.mainloop()
