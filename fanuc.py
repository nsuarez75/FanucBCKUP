from ftplib import FTP
import re
import os
from time import sleep
from progress.bar import Bar
import pickle
from datetime import datetime, date


def clear():  # limpiar consola
    os.system('cls')


def guardar_pickle(obj):  # guardar pickle
    try:
        with open("robots.pickle", "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def leer_pickle():  # leer pickle
    try:
        with open("robots.pickle", "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)


def crear_robot():  # creacion diccionario robot
    nombre = input("Nombre del robot: ")
    ip = input("IP del robot: ")
    plc = input("Numero de PLC: ")

    return {"nombre": nombre, "ip": ip, "plc": plc}


def borrar_robot():  # borra robot del pickle
    if os.path.exists("robots.pickle"):
        listar_robots()
        print("---------------------------------")
        nombre = input("Robot a borrar: ")
        robots = leer_pickle()
        for robot in robots:
            if robot['nombre'] == nombre:
                robots.remove(robot)
                break
        guardar_pickle(robots)


def añadir_robot(nuevo_robot):  # añadir robot al pickle
    if os.path.exists("robots.pickle"):
        robots = leer_pickle()
        robots.append(nuevo_robot)
        guardar_pickle(robots)
    else:
        guardar_pickle([nuevo_robot])


def listar_robots():  # Listar robots ordenados por PLC
    plcs = []
    robots = leer_pickle()
    for robot in robots:
        if robot['plc'] not in plcs:
            plcs.append(robot['plc'])
    plcs.sort()

    for plc in plcs:
        print("---------------------------------")
        print(f"PLC {plc}")

        for robot in robots:
            if robot['plc'] == plc:
                print(
                    f"Robot: {robot['nombre']} | IP: {robot['ip']} | PLC: {robot['plc']}")


def listar_robots_plc(plc):  # listar robots de un solo PLC
    robots = leer_pickle()
    print("-----------------------")
    for robot in robots:
        if robot['plc'] == plc:
            print(
                f"Robot: {robot['nombre']} | IP: {robot['ip']} | PLC: {robot['plc']}")
    print("-----------------------")


def listar_plcs():  # listar plcs disponibles
    plcs = []
    for robot in leer_pickle():
        if robot['plc'] not in plcs:
            plcs.append(robot['plc'])
    plcs.sort()
    print("-----------------------")
    for plc in plcs:
        print(f"PLC{plc}")
        print("-----------------------")


def backup_todos(plc):  # hacer backup robots
    robots = leer_pickle()
    completados = []
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M")
    carpeta_raiz = f"{desktop}\\Backup_PLC{plc}_{dt_string}"
    os.mkdir(carpeta_raiz)

    for robot in robots:
        clear()
        if completados != []:
            print("Progreso...")
            for comp in completados:
                print("------------------------")
                print(f"{comp}.... Finalizado")

        if robot['plc'] == plc:
            try:
                print(f"Conectandose a {robot['nombre']}")
                ftp = FTP(robot['ip'])
                ftp.login()
                carpeta_robot = f"{carpeta_raiz}\\{robot['nombre']}"
                os.mkdir(carpeta_robot)

                archivos = ftp.nlst()
                print("Conectado!")
                cantidad = 0
                for archivo in archivos:
                    cantidad += 1

                with Bar('Descargando archivos', max=cantidad) as bar:
                    for archivo in archivos:
                        with open(carpeta_robot + "\\" + archivo, "wb") as file:
                            ftp.retrbinary(f"RETR {archivo}", file.write)
                        bar.next()

                ftp.close()
                ftp = None
                completados.append(robot['nombre'])

            except Exception as e:
                print(f"Error haciendo backup de {robot['nombre']}: {e}")
                input()
    input("Backup completado....")


def backup_individual(plc, nombre):  # hacer backup de un robot
    robots = leer_pickle()
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M")

    for robot in robots:
        clear()
        if (robot['plc'] == plc) and (robot['nombre'] == nombre):
            try:
                print(f"Conectandose a {robot['nombre']}")
                ftp = FTP(robot['ip'])
                ftp.login()
                carpeta_robot = f"{desktop}\\{robot['nombre']}_{dt_string}"
                os.mkdir(carpeta_robot)

                archivos = ftp.nlst()
                print("Conectado!")
                cantidad = 0
                for archivo in archivos:
                    cantidad += 1

                with Bar('Descargando archivos', max=cantidad) as bar:
                    for archivo in archivos:
                        with open(carpeta_robot + "\\" + archivo, "wb") as file:
                            ftp.retrbinary(f"RETR {archivo}", file.write)
                        bar.next()

                ftp.close()
                ftp = None
                break
            except Exception as e:
                print(f"Error haciendo backup de {robot['nombre']}: {e}")
                input()
    input("Backup completado....")


if __name__ == "__main__":

    opcion = ""
    menu = "base"

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    while True:

        if menu == "base":

            if opcion == "":
                clear()
                print("Mejor que ir de teach en teach con el usb no?\n")
                print("[1] Hacer backup")
                print("[2] Listar robots")
                print("[3] Añadir robot")
                print("[4] Borrar robot")

                opcion = input("Comando: ")

            if opcion == "1":
                clear()
                menu = "backup"
                opcion = ""

            if opcion == "2":
                clear()
                listar_robots()
                input()
                opcion = ""

            if opcion == "3":
                clear()
                añadir_robot(crear_robot())
                clear()
                print("Robot añadido.")
                input()
                opcion = ""

            if opcion == "4":
                clear()
                borrar_robot()
                clear()
                print("Robot borrado.")
                input()
                opcion = ""

        if menu == "backup":

            if opcion == "":
                clear()
                print("Opciones backup\n")
                print("[1] Todos los robots")
                print("[2] Seleccionar robot")
                print("[3] Atras")

                opcion = input("Comando: ")

            if opcion == "1":
                clear()
                listar_plcs()
                plc = input("Seleccion PLC: ")
                backup_todos(plc)
                menu = "base"
                opcion = ""

            if opcion == "2":
                clear()
                listar_plcs()
                plc = input("Seleccion PLC: ")
                clear()
                listar_robots_plc(plc)
                nombre = input("Seleccion robot: ")
                backup_individual(plc, nombre)
                menu = "base"
                opcion = ""

            if opcion == "3":
                menu = "base"
                opcion = ""
