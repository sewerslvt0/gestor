import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import os
import json
from datetime import datetime, timedelta

DIRECTORIO_DATOS = "ordenes_compra"
if not os.path.exists(DIRECTORIO_DATOS):
    os.makedirs(DIRECTORIO_DATOS)

COLOR_PRINCIPAL = "#1E90FF"
COLOR_ADVERTENCIA = "#FFFF00"

def guardar_orden(nombre_proveedor, id_orden, cantidad_facturas, facturas, mes_vencimiento):
    datos = {
        "nombre_proveedor": nombre_proveedor,
        "id_orden": id_orden,
        "cantidad_facturas": cantidad_facturas,
        "facturas": facturas,
        "mes_vencimiento": mes_vencimiento,
        "ultima_modificacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    ruta_archivo = os.path.join(DIRECTORIO_DATOS, f"orden_{id_orden}.json")
    with open(ruta_archivo, 'w') as archivo:
        json.dump(datos, archivo)

def eliminar_orden(id_orden):
    confirmar = messagebox.askyesno("Eliminar Orden", f"¿Estás seguro que quieres eliminar la Orden {id_orden}?")
    if confirmar:
        ruta_archivo = os.path.join(DIRECTORIO_DATOS, f"orden_{id_orden}.json")
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
            actualizar_interfaz()
            messagebox.showinfo("Info", f"Orden {id_orden} eliminada correctamente.")
        else:
            messagebox.showerror("Error", f"El archivo de la orden {id_orden} no se encontró.")

def cargar_ordenes():
    ordenes = []
    for nombre_archivo in os.listdir(DIRECTORIO_DATOS):
        if nombre_archivo.endswith(".json"):
            with open(os.path.join(DIRECTORIO_DATOS, nombre_archivo), 'r') as archivo:
                ordenes.append(json.load(archivo))
    return ordenes

def esta_vencida(ultima_modificacion):
    fecha_actual = datetime.now()
    fecha_ultima_modificacion = datetime.strptime(ultima_modificacion, '%Y-%m-%d %H:%M:%S')
    diferencia_dias = (fecha_actual - fecha_ultima_modificacion).days
    return diferencia_dias > 30

def actualizar_interfaz():
    for widget in frame.winfo_children():
        widget.destroy()
    ordenes = cargar_ordenes()
    for orden in ordenes:
        fila = tk.Frame(frame, bg="white", padx=12, pady=5)
        fila.pack(fill=tk.X)
        
        vencida = esta_vencida(orden['ultima_modificacion'])
        color_texto = COLOR_ADVERTENCIA if vencida else COLOR_PRINCIPAL
        
        etiqueta_id_orden = tk.Label(fila, text="Orden:", font=("Arial", 12), fg=color_texto)
        etiqueta_proveedor = tk.Label(fila, text="Proveedor:", font=("Arial", 12), fg=color_texto)
        etiqueta_mes_vencimiento = tk.Label(fila, text="Mes Vencimiento:", font=("Arial", 12), fg=color_texto)
        etiqueta_facturas = tk.Label(fila, text="Facturas:", font=("Arial", 12), fg=color_texto)
        
        etiqueta_id_orden.pack(side=tk.LEFT)
        tk.Label(fila, text=f"{orden['id_orden']}", font=("Arial", 12), fg=color_texto).pack(side=tk.LEFT)
        etiqueta_proveedor.pack(side=tk.LEFT, padx=12)
        tk.Label(fila, text=f"{orden['nombre_proveedor']}", font=("Arial", 12), fg=color_texto).pack(side=tk.LEFT)
        etiqueta_mes_vencimiento.pack(side=tk.LEFT, padx=12)
        tk.Label(fila, text=f"{orden.get('mes_vencimiento', 'No especificado')}", font=("Arial", 12), fg=color_texto).pack(side=tk.LEFT)
        
        etiqueta_facturas.pack(side=tk.LEFT, padx=12)
        
        cantidad_facturas = orden['cantidad_facturas']
        total_facturas = cantidad_facturas
        facturas_completadas = sum(1 for valor in orden['facturas'].values() if valor)

        if total_facturas > 0:
            porcentaje = int((facturas_completadas / total_facturas) * 100)
            tk.Label(fila, text=f"{cantidad_facturas} ({porcentaje}%)", font=("Arial", 12), fg=color_texto).pack(side=tk.LEFT)
        else:
            tk.Label(fila, text=f"{cantidad_facturas}", font=("Arial", 12), fg=color_texto).pack(side=tk.LEFT)

        boton_editar = tk.Button(fila, text="Editar Facturas", bg=COLOR_PRINCIPAL, fg="white", font=("Arial", 10), command=lambda oid=orden['id_orden'], ic=orden['cantidad_facturas']: editar_facturas(oid, ic))
        boton_editar.pack(side=tk.RIGHT, padx=10)
        boton_eliminar = tk.Button(fila, text="Eliminar", bg=COLOR_PRINCIPAL, fg="white", font=("Arial", 10), command=lambda oid=orden['id_orden']: eliminar_orden(oid))
        boton_eliminar.pack(side=tk.RIGHT, padx=10)


def agregar_orden():
    nombre_proveedor = simpledialog.askstring("Input", "Ingrese el nombre del proveedor")
    id_orden = simpledialog.askinteger("Input", "Ingrese número de la orden")
    cantidad_facturas = simpledialog.askinteger("Input", "Ingrese cantidad de facturas")
    mes_vencimiento = simpledialog.askstring("Input", "Ingrese el mes de vencimiento (Ejemplo: Enero, Febrero, Marzo, etc.)")
    facturas = {str(i): "" for i in range(1, cantidad_facturas + 1)}
    if nombre_proveedor and id_orden is not None and cantidad_facturas is not None and mes_vencimiento:
        guardar_orden(nombre_proveedor, id_orden, cantidad_facturas, facturas, mes_vencimiento)
        actualizar_interfaz()

def editar_facturas(id_orden, cantidad_facturas):
    ventana_facturas = tk.Toplevel()
    ventana_facturas.title(f"Editar Facturas para Orden {id_orden}")
    ventana_facturas.geometry("300x300")
    ventana_facturas.config(bg="white")

    ordenes = cargar_ordenes()
    for orden in ordenes:
        if orden['id_orden'] == id_orden:
            facturas = orden['facturas']
            break

    entradas_facturas = []
    for i in range(1, cantidad_facturas + 1):
        etiqueta_factura = tk.Label(ventana_facturas, text=f"{i} Mes: ", bg="white", fg=COLOR_PRINCIPAL, font=("Arial", 10))
        etiqueta_factura.grid(row=i, column=0)
        entrada_factura = tk.Entry(ventana_facturas)
        entrada_factura.grid(row=i, column=1)
        entrada_factura.insert(tk.END, facturas.get(str(i), ""))
        entradas_facturas.append(entrada_factura)

    def guardar_facturas():
        nuevas_facturas = {str(i): entrada.get() for i, entrada in enumerate(entradas_facturas, start=1)}
        for orden in ordenes:
            if orden['id_orden'] == id_orden:
                guardar_orden(orden['nombre_proveedor'], id_orden, cantidad_facturas, nuevas_facturas, orden['mes_vencimiento'])
                break
        ventana_facturas.destroy()
        actualizar_interfaz()

    boton_guardar = tk.Button(ventana_facturas, text="Guardar", bg=COLOR_PRINCIPAL, fg="white", font=("Arial", 8), command=guardar_facturas)
    boton_guardar.grid(row=cantidad_facturas + 1, columnspan=2)
#Ventana
root = tk.Tk()
root.title("Gestor de Órdenes de Compra")
root.geometry("1200x800")
root.config(bg="white")

#Imagen
ruta_imagen = "OIP-_12_.png"
if os.path.exists(ruta_imagen):
    try:
        img = Image.open(ruta_imagen)
        img = img.resize((200, 200))
        foto = ImageTk.PhotoImage(img)
        etiqueta_imagen = tk.Label(root, image=foto, bg="white")
        etiqueta_imagen.image = foto
        etiqueta_imagen.pack(side=tk.RIGHT, padx=20, pady=20)
    except Exception as e:
        print("Error al abrir la imagen:", e)
else:
    print("La ruta de la imagen no es válida o el archivo no existe.")

frame = tk.Frame(root, bg="white")
frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

actualizar_interfaz()

boton_agregar = tk.Button(root, text="Ingresar Orden de Compra", bg=COLOR_PRINCIPAL, fg="white", font=("Arial", 10), command=agregar_orden)
boton_agregar.pack(pady=10)

root.mainloop()
