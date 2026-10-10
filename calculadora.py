"""Calculadora gráfica básica em Python (tkinter).

Executar:  python calculadora.py
Suporta mouse e teclado (dígitos, + - * / %, Enter, Backspace, Esc).
"""

import ast
import operator
import re
import tkinter as tk

# ---------- Avaliação segura de expressões (sem usar eval) ----------

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def avaliar(expressao: str):
    """Avalia uma expressão aritmética permitindo apenas números e operadores."""

    def _eval(no):
        if isinstance(no, ast.Expression):
            return _eval(no.body)
        if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
            return no.value
        if isinstance(no, ast.BinOp) and type(no.op) in OPERADORES:
            return OPERADORES[type(no.op)](_eval(no.left), _eval(no.right))
        if isinstance(no, ast.UnaryOp) and type(no.op) in OPERADORES:
            return OPERADORES[type(no.op)](_eval(no.operand))
        raise ValueError("Expressão inválida")

    return _eval(ast.parse(expressao, mode="eval"))


def formatar(numero) -> str:
    if isinstance(numero, float):
        if numero.is_integer() and abs(numero) < 1e15:
            return str(int(numero))
        return format(numero, ".10g")
    return str(numero)


# ---------- Interface gráfica ----------

OPS = "+−×÷%"

COR_FUNDO = "#1e1e2e"
COR_DISPLAY = "#181825"
COR_TEXTO = "#cdd6f4"
COR_NUMERO = "#313244"
COR_NUMERO_HOVER = "#45475a"
COR_OPERADOR = "#fab387"
COR_OPERADOR_HOVER = "#f9c9a8"
COR_ESPECIAL = "#585b70"
COR_ESPECIAL_HOVER = "#6c7086"
COR_IGUAL = "#a6e3a1"
COR_IGUAL_HOVER = "#c0eebc"

# (rótulo, linha, coluna, colunas ocupadas, tipo)
BOTOES = [
    ("C", 0, 0, 1, "especial"), ("⌫", 0, 1, 1, "especial"),
    ("%", 0, 2, 1, "operador"), ("÷", 0, 3, 1, "operador"),
    ("7", 1, 0, 1, "numero"), ("8", 1, 1, 1, "numero"),
    ("9", 1, 2, 1, "numero"), ("×", 1, 3, 1, "operador"),
    ("4", 2, 0, 1, "numero"), ("5", 2, 1, 1, "numero"),
    ("6", 2, 2, 1, "numero"), ("−", 2, 3, 1, "operador"),
    ("1", 3, 0, 1, "numero"), ("2", 3, 1, 1, "numero"),
    ("3", 3, 2, 1, "numero"), ("+", 3, 3, 1, "operador"),
    ("0", 4, 0, 2, "numero"), (".", 4, 2, 1, "numero"),
    ("=", 4, 3, 1, "igual"),
]

CORES = {
    "numero": (COR_NUMERO, COR_NUMERO_HOVER, COR_TEXTO),
    "operador": (COR_OPERADOR, COR_OPERADOR_HOVER, COR_FUNDO),
    "especial": (COR_ESPECIAL, COR_ESPECIAL_HOVER, COR_TEXTO),
    "igual": (COR_IGUAL, COR_IGUAL_HOVER, COR_FUNDO),
}


class Calculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora")
        self.configure(bg=COR_FUNDO, padx=12, pady=12)
        self.resizable(False, False)

        self.expressao = ""
        self.limpar_na_proxima = False  # True após "=" ou erro
        self.texto_display = tk.StringVar(value="0")

        self._criar_display()
        self._criar_botoes()
        self.bind("<Key>", self._tecla)

    # --- construção da interface ---

    def _criar_display(self):
        tk.Label(
            self,
            textvariable=self.texto_display,
            anchor="e",
            bg=COR_DISPLAY,
            fg=COR_TEXTO,
            font=("Segoe UI", 28),
            width=14,
            padx=12,
            pady=18,
        ).grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0, 10))

    def _criar_botoes(self):
        for rotulo, linha, coluna, span, tipo in BOTOES:
            fundo, hover, texto = CORES[tipo]
            botao = tk.Button(
                self,
                text=rotulo,
                font=("Segoe UI", 16, "bold"),
                bg=fundo,
                fg=texto,
                activebackground=hover,
                activeforeground=texto,
                relief="flat",
                bd=0,
                width=4 * span + (span - 1) * 1,
                height=2,
                command=lambda r=rotulo: self.pressionar(r),
            )
            botao.grid(
                row=linha + 1, column=coluna, columnspan=span,
                sticky="nsew", padx=3, pady=3,
            )
            botao.bind("<Enter>", lambda e, b=botao, c=hover: b.config(bg=c))
            botao.bind("<Leave>", lambda e, b=botao, c=fundo: b.config(bg=c))

        for i in range(4):
            self.columnconfigure(i, weight=1, uniform="col")

    # --- lógica ---

    def pressionar(self, valor: str):
        if valor == "C":
            self.expressao = ""
            self.limpar_na_proxima = False
        elif valor == "⌫":
            if self.limpar_na_proxima:
                self.expressao = ""
                self.limpar_na_proxima = False
            else:
                self.expressao = self.expressao[:-1]
        elif valor == "=":
            self._calcular()
            return
        else:
            self._inserir(valor)
        self._atualizar_display()

    def _inserir(self, valor: str):
        if self.limpar_na_proxima:
            # Após um resultado, operador continua a conta; número começa outra.
            if valor not in OPS:
                self.expressao = ""
            self.limpar_na_proxima = False

        if valor in OPS:
            if not self.expressao:
                if valor == "−":  # permite número negativo no início
                    self.expressao = "−"
                return
            if self.expressao == "−":
                return
            if self.expressao[-1] in OPS:  # troca o operador anterior
                self.expressao = self.expressao[:-1]
            self.expressao += valor
            return

        segmento = re.split(r"[+−×÷%]", self.expressao)[-1]

        if valor == ".":
            if "." in segmento:
                return
            self.expressao += "0." if segmento == "" else "."
            return

        # dígito: evita zeros à esquerda (007)
        if segmento == "0":
            self.expressao = self.expressao[:-1] + valor
        else:
            self.expressao += valor

    def _calcular(self):
        if not self.expressao:
            return
        expr = self.expressao
        while expr and expr[-1] in OPS + "−":
            expr = expr[:-1]
        if not expr:
            return

        codigo = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        try:
            resultado = formatar(avaliar(codigo))
            self.expressao = resultado.replace("-", "−")
            self.texto_display.set(self._cortar(self.expressao))
        except ZeroDivisionError:
            self.expressao = ""
            self.texto_display.set("Divisão por zero")
        except Exception:
            self.expressao = ""
            self.texto_display.set("Erro")
        self.limpar_na_proxima = True

    def _atualizar_display(self):
        self.texto_display.set(self._cortar(self.expressao) if self.expressao else "0")

    @staticmethod
    def _cortar(texto: str, limite: int = 14) -> str:
        return texto if len(texto) <= limite else "…" + texto[-(limite - 1):]

    # --- teclado ---

    def _tecla(self, evento):
        mapa = {"*": "×", "/": "÷", "-": "−", ",": ".", "=": "="}
        char = evento.char
        if evento.keysym in ("Return", "KP_Enter"):
            self.pressionar("=")
        elif evento.keysym == "BackSpace":
            self.pressionar("⌫")
        elif evento.keysym == "Escape":
            self.pressionar("C")
        elif char and char in "0123456789.+%":
            self.pressionar(char)
        elif char in mapa:
            self.pressionar(mapa[char])


if __name__ == "__main__":
    Calculadora().mainloop()
