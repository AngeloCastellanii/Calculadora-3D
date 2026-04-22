import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Configuración Visual de la Ventana ---
ctk.set_appearance_mode("dark")  # Modo oscuro profesional
ctk.set_default_color_theme("blue")

class Studio3MFApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Studio3MF Calculadora 3D - Nivel Profesional")
        self.geometry("950x650")
        self.minsize(900, 600)

        # Configuración de la cuadrícula principal (2 columnas)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO (Entradas) =================
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame_inputs.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_inputs, text="Parámetros del Proyecto", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(15, 20))

        # Diccionario para guardar los inputs
        self.entradas = {}
        
        # Lista de campos: (Etiqueta, Valor por defecto)
        campos = [
            ("Precio Filamento (1kg) [$]:", "25.0"),
            ("Peso de la pieza [g]:", "0.0"),
            ("Margen de Fallo/Soportes [%]:", "5.0"),
            ("Tiempo de Impresión [h]:", "0.0"),
            ("Tarifa Eléctrica [$/kWh]:", "0.50"),
            ("Consumo Máquina [kW]:", "0.35"),
            ("Desgaste/Amortización [$/h]:", "0.14"),
            ("Horas Manuales (Limpieza/Corte) [h]:", "2.0"),
            ("Tu Tarifa por Hora [$/h]:", "10.0"),
            ("Multiplicador de Ganancia [x]:", "3.5")
        ]

        for i, (texto, valor_defecto) in enumerate(campos):
            ctk.CTkLabel(self.frame_inputs, text=texto, font=ctk.CTkFont(size=13)).grid(row=i+1, column=0, padx=15, pady=8, sticky="w")
            entry = ctk.CTkEntry(self.frame_inputs, width=100)
            entry.insert(0, valor_defecto)
            entry.grid(row=i+1, column=1, padx=15, pady=8, sticky="e")
            self.entradas[texto] = entry

        # Botón Calcular
        self.btn_calcular = ctk.CTkButton(self.frame_inputs, text="CALCULAR PRECIO", command=self.calcular_precio, font=ctk.CTkFont(size=15, weight="bold"), height=40)
        self.btn_calcular.grid(row=len(campos)+1, column=0, columnspan=2, pady=25)

        # ================= PANEL DERECHO (Resultados y Gráfica) =================
        self.frame_results = ctk.CTkFrame(self)
        self.frame_results.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_results, text="Desglose Financiero", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 10))

        # Modo para mostrar solo el precio al cliente
        self.modo_cliente_var = ctk.BooleanVar(value=False)
        self.switch_modo_cliente = ctk.CTkSwitch(
            self.frame_results,
            text="Modo Cliente (solo precio)",
            variable=self.modo_cliente_var,
            command=self.actualizar_vista_cliente,
            font=ctk.CTkFont(size=13)
        )
        self.switch_modo_cliente.pack(pady=(0, 10))

        # Labels para resultados
        self.lbl_costo_base = ctk.CTkLabel(self.frame_results, text="Costo Base: $0.00", font=ctk.CTkFont(size=15))
        self.lbl_costo_base.pack(pady=5)
        
        self.lbl_mano_obra = ctk.CTkLabel(self.frame_results, text="Mano de Obra: $0.00", font=ctk.CTkFont(size=15))
        self.lbl_mano_obra.pack(pady=5)

        # Área para la gráfica de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_results)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Precio sugerido al final: queda debajo de estadísticas/gráfica
        self.lbl_precio_final = ctk.CTkLabel(self.frame_results, text="PRECIO SUGERIDO: $0.00", font=ctk.CTkFont(size=22, weight="bold"), text_color="#2FA572")
        self.lbl_precio_final.pack(pady=(0, 15))
        
        # Dibujar gráfica vacía al inicio
        self.ax.axis('off')
        self.fig.tight_layout()

    def actualizar_vista_cliente(self):
        solo_precio = self.modo_cliente_var.get()
        if solo_precio:
            self.lbl_costo_base.pack_forget()
            self.lbl_mano_obra.pack_forget()
            self.canvas.get_tk_widget().pack_forget()
            self.lbl_precio_final.configure(font=ctk.CTkFont(size=30, weight="bold"))
        else:
            self.lbl_costo_base.pack(pady=5)
            self.lbl_mano_obra.pack(pady=5)
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            self.lbl_precio_final.configure(font=ctk.CTkFont(size=22, weight="bold"))

        # Mantener el precio al final del panel en ambos modos
        self.lbl_precio_final.pack_forget()
        self.lbl_precio_final.pack(pady=(0, 15))

    def calcular_precio(self):
        try:
            # 1. Obtener valores de los inputs
            p_filamento = float(self.entradas["Precio Filamento (1kg) [$]:"].get())
            peso = float(self.entradas["Peso de la pieza [g]:"].get())
            fallo = float(self.entradas["Margen de Fallo/Soportes [%]:"].get()) / 100
            tiempo = float(self.entradas["Tiempo de Impresión [h]:"].get())
            tarifa_luz = float(self.entradas["Tarifa Eléctrica [$/kWh]:"].get())
            consumo_kw = float(self.entradas["Consumo Máquina [kW]:"].get())
            desgaste_h = float(self.entradas["Desgaste/Amortización [$/h]:"].get())
            h_manuales = float(self.entradas["Horas Manuales (Limpieza/Corte) [h]:"].get())
            tarifa_h = float(self.entradas["Tu Tarifa por Hora [$/h]:"].get())
            multiplicador = float(self.entradas["Multiplicador de Ganancia [x]:"].get())

            # 2. Cálculos Matemáticos (Modelo Híbrido)
            costo_material = (p_filamento / 1000) * peso * (1 + fallo)
            costo_electricidad = tiempo * consumo_kw * tarifa_luz
            costo_desgaste = tiempo * desgaste_h
            costo_operativo = costo_electricidad + costo_desgaste
            
            costo_base_fisico = costo_material + costo_operativo
            costo_mano_obra = h_manuales * tarifa_h
            
            precio_final = (costo_base_fisico * multiplicador) + costo_mano_obra
            ganancia_neta = precio_final - (costo_base_fisico + costo_mano_obra)

            # 3. Actualizar Textos
            self.lbl_costo_base.configure(text=f"Costo Físico (Mat + Máq): ${costo_base_fisico:.2f}")
            self.lbl_mano_obra.configure(text=f"Mano de Obra (Tus Horas): ${costo_mano_obra:.2f}")
            self.lbl_precio_final.configure(text=f"PRECIO SUGERIDO: ${precio_final:.2f} USD")

            # 4. Actualizar Gráfica
            self.ax.clear()
            etiquetas = ['Material', 'Operativo', 'Tu Tiempo', 'Ganancia Neta']
            valores = [costo_material, costo_operativo, costo_mano_obra, ganancia_neta]
            colores = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
            
            # Formato del texto en pastel (texto blanco)
            textprops = {"color": "white", "weight": "bold"}
            
            self.ax.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=140, colors=colores, textprops=textprops)
            self.ax.set_title("Distribución del Precio Final", color="white", pad=10)
            self.fig.patch.set_facecolor('#2b2b2b') # Fondo oscuro
            self.fig.tight_layout()
            
            self.canvas.draw()

        except ValueError:
            self.lbl_precio_final.configure(text="Error: Revisa los números", text_color="red")

if __name__ == "__main__":
    app = Studio3MFApp()
    app.mainloop()