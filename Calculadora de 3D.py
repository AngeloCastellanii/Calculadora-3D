import tkinter as tk
from tkinter import messagebox, ttk


PESO_TOTAL_BOBINA_G = 1000.0
CONSUMO_WATTS = 350.0
COSTO_REPUESTO_USD = 20.0
VIDA_UTIL_REPUESTO_H = 500.0


def parsear_numero(valor_texto):
    """Acepta punto o coma decimal y devuelve float."""
    valor_limpio = valor_texto.strip().replace(",", ".")
    if not valor_limpio:
        raise ValueError("Campo vacio")
    return float(valor_limpio)


class Studio3MFCalculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Studio3MF calculadora")
        self.geometry("760x560")
        self.minsize(720, 520)
        self.configure(bg="#f3f5f7")

        self._crear_ui()

    def _crear_ui(self):
        marco = tk.Frame(self, bg="#f3f5f7", padx=18, pady=16)
        marco.pack(fill="both", expand=True)

        titulo = tk.Label(
            marco,
            text="Studio3MF calculadora",
            font=("Segoe UI", 18, "bold"),
            bg="#f3f5f7",
            fg="#1f2937",
        )
        titulo.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        subtitulo = tk.Label(
            marco,
            text="Calculadora de costos para impresiones 3D",
            font=("Segoe UI", 10),
            bg="#f3f5f7",
            fg="#4b5563",
        )
        subtitulo.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 16))

        self.entradas = {}

        campos = [
            ("Precio de filamento (bobina 1kg) en USD", "precio_bobina", "20"),
            ("Peso de la pieza a imprimir (g)", "peso_pieza", "100"),
            ("Tiempo total de impresion (h)", "tiempo_horas", "4"),
            ("Tarifa electrica local (USD/kWh)", "tarifa_electrica", "0.12"),
        ]

        fila_base = 2
        for i, (etiqueta, clave, valor_defecto) in enumerate(campos):
            tk.Label(
                marco,
                text=etiqueta,
                font=("Segoe UI", 10),
                bg="#f3f5f7",
                fg="#111827",
            ).grid(row=fila_base + i, column=0, sticky="w", pady=5)

            entrada = tk.Entry(marco, font=("Segoe UI", 10), width=24)
            entrada.insert(0, valor_defecto)
            entrada.grid(row=fila_base + i, column=1, sticky="w", pady=5, padx=(8, 0))
            self.entradas[clave] = entrada

        fila_multiplicador = fila_base + len(campos)
        tk.Label(
            marco,
            text="Ganancia por multiplicador (x2 minimo)",
            font=("Segoe UI", 10),
            bg="#f3f5f7",
            fg="#111827",
        ).grid(row=fila_multiplicador, column=0, sticky="w", pady=5)

        self.multiplicador_var = tk.StringVar(value="2")
        self.multiplicador_selector = ttk.Combobox(
            marco,
            textvariable=self.multiplicador_var,
            values=["2", "3", "4", "5", "6", "7", "8", "10"],
            width=22,
        )
        self.multiplicador_selector.grid(row=fila_multiplicador, column=1, sticky="w", pady=5, padx=(8, 0))
        self.multiplicador_selector.set("2")

        tk.Label(
            marco,
            text=(
                "Valores fijos: bobina total 1000 g | consumo 350 W "
                "| repuesto 20 USD | vida util 500 h"
            ),
            font=("Segoe UI", 9, "italic"),
            bg="#f3f5f7",
            fg="#6b7280",
        ).grid(row=fila_multiplicador + 1, column=0, columnspan=3, sticky="w", pady=(10, 12))

        botones = tk.Frame(marco, bg="#f3f5f7")
        botones.grid(row=fila_multiplicador + 2, column=0, columnspan=3, sticky="w")

        tk.Button(
            botones,
            text="Calcular",
            font=("Segoe UI", 10, "bold"),
            bg="#0b5ed7",
            fg="white",
            padx=14,
            pady=6,
            command=self.calcular,
            relief="flat",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            botones,
            text="Limpiar",
            font=("Segoe UI", 10),
            bg="#e5e7eb",
            fg="#111827",
            padx=12,
            pady=6,
            command=self.limpiar_resultado,
            relief="flat",
        ).pack(side="left")

        self.resultado = tk.Text(
            marco,
            height=14,
            width=82,
            font=("Consolas", 10),
            bg="white",
            fg="#111827",
            relief="solid",
            bd=1,
        )
        self.resultado.grid(
            row=fila_multiplicador + 3,
            column=0,
            columnspan=3,
            sticky="nsew",
            pady=(12, 0),
        )
        self.resultado.insert(
            "1.0",
            "Ingresa tus datos y presiona 'Calcular' para obtener el costo de impresion.",
        )
        self.resultado.config(state="disabled")

        marco.columnconfigure(2, weight=1)
        marco.rowconfigure(fila_multiplicador + 3, weight=1)

    def limpiar_resultado(self):
        self._actualizar_resultado("Resultado limpiado. Ingresa valores y vuelve a calcular.")

    def _actualizar_resultado(self, texto):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", tk.END)
        self.resultado.insert("1.0", texto)
        self.resultado.config(state="disabled")

    def calcular(self):
        try:
            precio_bobina = parsear_numero(self.entradas["precio_bobina"].get())
            peso_pieza = parsear_numero(self.entradas["peso_pieza"].get())
            tiempo_horas = parsear_numero(self.entradas["tiempo_horas"].get())
            tarifa_electrica = parsear_numero(self.entradas["tarifa_electrica"].get())
            multiplicador = parsear_numero(self.multiplicador_var.get())

            if any(v < 0 for v in [precio_bobina, peso_pieza, tiempo_horas, tarifa_electrica]):
                raise ValueError("No se permiten valores negativos")
            if multiplicador < 2:
                raise ValueError("El multiplicador minimo es x2")

            costo_material = (precio_bobina / PESO_TOTAL_BOBINA_G) * peso_pieza
            costo_filamento_gramo = precio_bobina / PESO_TOTAL_BOBINA_G
            consumo_kw = CONSUMO_WATTS / 1000.0
            costo_electrico = consumo_kw * tiempo_horas * tarifa_electrica
            costo_repuesto_hora = COSTO_REPUESTO_USD / VIDA_UTIL_REPUESTO_H
            costo_desgaste = costo_repuesto_hora * tiempo_horas

            costo_base = costo_material + costo_electrico + costo_desgaste
            precio_final = costo_base * multiplicador
            ganancia = precio_final - costo_base

            lineas = [
                "DESGLOSE DE COSTOS - Studio3MF",
                "=" * 44,
                f"Precio filamento bobina:     ${precio_bobina:,.2f} USD",
                f"Costo filamento por gramo:   ${costo_filamento_gramo:,.4f} USD",
                f"Costo material (pieza):      ${costo_material:,.2f} USD",
                f"Costo electricidad:          ${costo_electrico:,.2f} USD",
                f"Desgaste repuesto:           ${costo_desgaste:,.2f} USD",
                "-" * 44,
                f"COSTO BASE:                  ${costo_base:,.2f} USD",
                f"Multiplicador aplicado:      x{multiplicador:.2f}",
                f"Ganancia estimada:           ${ganancia:,.2f} USD",
                "=" * 44,
                f"PRECIO FINAL SUGERIDO:       ${precio_final:,.2f} USD",
            ]
            salida = "\n".join(lineas)

            self._actualizar_resultado(salida)

        except ValueError:
            messagebox.showerror(
                "Dato invalido",
                "Revisa los campos: solo se permiten numeros positivos.\n"
                "El multiplicador de ganancia debe ser x2 o mayor.\n"
                "Puedes usar punto o coma decimal.",
            )


if __name__ == "__main__":
    app = Studio3MFCalculadora()
    app.mainloop()

        