import csv
import os
import pandas as pd
from datetime import datetime
import qrcode
import random

ARCHIVO = "usuarios.csv"
REGISTROS = "registros.csv"
CARPETA_QR = "qrs"

def crear_archivo_si_no_existe():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, mode="w", newline="", encoding="utf-8") as file:
            escritor = csv.writer(file)
            escritor.writerow([
                "Cedula",
                "Nombre",
                "Apellido",
                "FechaNacimiento",
                "Edad",
                "MayorDeEdad",
                "HoraEntrada",
                "HoraSalida",
                "CodigoQR"
            ])
        print("Archivo 'usuarios.csv' creado correctamente.\n")

    if not os.path.exists(REGISTROS):
        with open(REGISTROS, mode="w", newline="", encoding="utf-8") as file:
            escritor = csv.writer(file)
            escritor.writerow(
                ["Cedula", "Nombre", "Apellido", "Accion", "FechaHora"])
        print("Archivo 'registros.csv' creado correctamente.\n")


def crear_carpeta_qr():
    if not os.path.exists(CARPETA_QR):
        os.makedirs(CARPETA_QR)


def generar_codigo_qr(cedula):
    random.seed(cedula)
    mezcla = list(cedula)
    random.shuffle(mezcla)
    codigo = "".join(mezcla) + str(random.randint(100, 999))
    return codigo

def registrar_usuario():
    nombre = input("Ingrese sus nombres: ")
    apellido = input("Ingrese sus apellidos: ")
    cedula = input("Ingrese su número de cedula: ")

    # VALIDACIÓN DE FECHA (YYYY-MM-DD)
    while True:
        fecha_nacimiento = input(
            "Ingrese su fecha de nacimiento (YYYY-MM-DD): ")

        try:
            fecha_dt = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
            break
        except ValueError:
            print("Formato incorrecto. Use el formato YYYY-MM-DD.")

    # CÁLCULO DE EDAD
    hoy = datetime.now()
    edad = hoy.year - fecha_dt.year - (
        (hoy.month, hoy.day) < (fecha_dt.month, fecha_dt.day)
    )

    mayor_edad = "Sí" if edad >= 18 else "No"

    if mayor_edad == "No":
        print("Acceso denegado. Debe ser mayor de edad para ingresar.")
        return

    codigo_qr = generar_codigo_qr(cedula)
    crear_carpeta_qr()
    img = qrcode.make(codigo_qr)
    qr_path = os.path.join(CARPETA_QR, f"QR_{cedula}.png")
    img.save(qr_path)

    with open(ARCHIVO, mode="a", newline="", encoding="utf-8") as file:
        escritor = csv.writer(file)
        escritor.writerow([
            cedula, nombre, apellido, fecha_nacimiento,
            edad, mayor_edad, "", "", codigo_qr
        ])

    print(f"QR generado y guardado en: {qr_path}")
    print(f"Usuario {nombre} {apellido} registrado correctamente.\n")


def registrar_entrada_salida():
    codigo = input(
        "Escanee su QR y ponga el codigo o ingrese su cedula: ").strip()

    if not os.path.exists(ARCHIVO):
        print("No hay registros todavia.")
        return

    df = pd.read_csv(ARCHIVO, dtype=str)

    if df.empty:
        print("No hay usuarios registrados.")
        return

    df.columns = df.columns.str.strip()
    df["Cedula"] = df["Cedula"].astype(str).str.strip()
    df["CodigoQR"] = df["CodigoQR"].astype(str).str.strip()

    usuario = df.loc[(df["Cedula"] == codigo) | (df["CodigoQR"] == codigo)]

    if usuario.empty:
        print("Usuario no registrado.")
        return

    index = usuario.index[0]
    nombre = df.at[index, "Nombre"]
    apellido = df.at[index, "Apellido"]
    cedula = df.at[index, "Cedula"]

    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if pd.isna(df.at[index, "HoraEntrada"]) or df.at[index, "HoraEntrada"] == "" or \
       (df.at[index, "HoraSalida"] != "" and not pd.isna(df.at[index, "HoraSalida"])):
        df.at[index, "HoraEntrada"] = hora_actual
        df.at[index, "HoraSalida"] = ""
        accion = "Entrada"
        print(
            f"Bienvenido {nombre} {apellido}! Hora de entrada: {hora_actual}")
    else:
        df.at[index, "HoraSalida"] = hora_actual
        accion = "Salida"
        print(
            f"Hasta luego {nombre} {apellido}! Hora de salida: {hora_actual}")

    with open(REGISTROS, mode="a", newline="", encoding="utf-8") as file:
        escritor = csv.writer(file)
        escritor.writerow([cedula, nombre, apellido, accion, hora_actual])

    df.to_csv(ARCHIVO, index=False)


def ver_aforo_actual():
    if not os.path.exists(ARCHIVO):
        print("No hay registros todavia.")
        return

    df = pd.read_csv(ARCHIVO, dtype=str)
    dentro = df[df["HoraEntrada"].notna() & (
        (df["HoraSalida"].isna()) | (df["HoraSalida"] == ""))]
    print(f"Aforo actual: {len(dentro)} personas dentro.\n")


def ver_historial():
    if not os.path.exists(REGISTROS):
        print("No hay historial registrado.")
        return

    df = pd.read_csv(REGISTROS, dtype=str)
    if df.empty:
        print("Aun no hay movimientos registrados.")
        return

    print("\n=== HISTORIAL DE ENTRADAS Y SALIDAS ===\n")
    print(df.to_string(index=False))
    print()


def limpiar_registros():
    confirmacion = input(
        "¿Seguro que desea borrar TODOS los registros? (s/n): ").strip().lower()
    if confirmacion != "s":
        print("Operacion cancelada.")
        return

    with open(ARCHIVO, mode="w", newline="", encoding="utf-8") as file:
        escritor = csv.writer(file)
        escritor.writerow([
            "Cedula",
            "Nombre",
            "Apellido",
            "FechaNacimiento",
            "Edad",
            "MayorDeEdad",
            "HoraEntrada",
            "HoraSalida",
            "CodigoQR"
        ])

    with open(REGISTROS, mode="w", newline="", encoding="utf-8") as file:
        escritor = csv.writer(file)
        escritor.writerow(
            ["Cedula", "Nombre", "Apellido", "Accion", "FechaHora"])

    print("Todos los registros fueron eliminados correctamente.\n")


def main():
    crear_archivo_si_no_existe()
    crear_carpeta_qr()

    while True:
        print("\n--- Control de Acceso Discoteca ---")
        print("1. Registrar nuevo usuario")
        print("2. Escanear QR / Registrar entrada o salida")
        print("3. Ver aforo actual")
        print("4. Ver historial completo")
        print("5. Limpiar todos los registros")
        print("6. Salir")
        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            registrar_entrada_salida()
        elif opcion == "3":
            ver_aforo_actual()
        elif opcion == "4":
            ver_historial()
        elif opcion == "5":
            limpiar_registros()
        elif opcion == "6":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
