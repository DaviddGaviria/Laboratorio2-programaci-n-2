import os

# Ruta a la carpeta donde tienes los archivos
ruta_archivos = "C:\\Users\\JULIAN\\Desktop\\proyecto_trivia"
archivo_usuarios = os.path.join(ruta_archivos, "usuarios_trivia.txt")

# Lista para mantener los usuarios conectados
usuarios_conectados = set()

# Función para cargar preguntas y respuestas desde los archivos
def loadTrivia():
    trivia = {}
    with open(os.path.join(ruta_archivos, "preguntas_trivia.txt"), "r", encoding='utf-8') as file_preguntas, \
         open(os.path.join(ruta_archivos, "respuestas_trivia.txt"), "r", encoding='utf-8') as file_respuestas:
        
        categoria = None
        for pregunta_linea, respuesta_linea in zip(file_preguntas, file_respuestas):
            pregunta_linea = pregunta_linea.strip()
            respuesta_linea = respuesta_linea.strip()
            if pregunta_linea.startswith("#"):  # Detectar nueva categoría
                categoria = pregunta_linea[1:].strip()
                trivia[categoria] = []
            elif categoria:
                pregunta, *opciones = pregunta_linea.split("|")
                trivia[categoria].append((pregunta, opciones, respuesta_linea.lower()))
    return trivia

# Función para registrar un nuevo usuario
def registerUser(usuarios):
    username = input("Crea tu nombre de usuario: ").strip()
    if username in usuarios:
        print("El usuario ya está registrado. Intenta iniciar sesión.")
        return None, usuarios
    
    password = input("Crea una contraseña: ").strip()
    usuarios[username] = {'password': password, 'correctas': 0, 'conectado': "conectado"}
    saveUsers(usuarios)
    print("Usuario registrado exitosamente.")
    usuarios_conectados.add(username)
    return username, usuarios

# Función para iniciar sesión
def loginUser(usuarios):
    username = input("Introduce tu nombre de usuario: ").strip()
    if username not in usuarios:
        print("El usuario no está registrado.")
        return None, usuarios
    
    password = input("Introduce tu contraseña: ").strip()
    if usuarios[username]['password'] == password:
        print("¡Inicio de sesión exitoso! Bienvenido, " + username)
        usuarios[username]['conectado'] = "conectado"  # Marcar como conectado
        saveUsers(usuarios)
        usuarios_conectados.add(username)  # Añadir a usuarios conectados
        return username, usuarios
    else:
        print("Contraseña incorrecta. Inténtalo de nuevo.")
        return None, usuarios

# Función para cargar usuarios desde el archivo
def loadUsers():
    usuarios = {}
    if os.path.exists(archivo_usuarios):
        with open(archivo_usuarios, "r", encoding='utf-8') as file:
            for linea in file:
                datos = linea.strip().split(",")
                if len(datos) == 3:  # Si faltan datos de estado de conexión
                    username, password, correctas = datos
                    conectado = "desconectado"  # Valor por defecto si no está presente
                elif len(datos) == 4:  # Si todos los datos están presentes
                    username, password, correctas, conectado = datos
                else:
                    print(f"Error: formato incorrecto en la línea: {linea}")
                    continue

                usuarios[username] = {
                    'password': password,
                    'correctas': int(correctas),
                    'conectado': conectado  # Guardamos el estado de conexión directamente
                }
    return usuarios

# Función para guardar usuarios y sus datos
def saveUsers(usuarios):
    with open(archivo_usuarios, "w", encoding='utf-8') as file:
        for username, info in usuarios.items():
            file.write(f"{username},{info['password']},{info['correctas']},{info['conectado']}\n")

# Función para mostrar la pregunta y sus opciones
def askQuestion(pregunta_info):
    pregunta, opciones, _ = pregunta_info
    print(f"Pregunta: {pregunta}")
    letras = ['a', 'b', 'c', 'd']
    for i, opcion in enumerate(opciones):
        print(f"{letras[i]}. {opcion}")

# Función que verifica si la respuesta es correcta
def checkAnswer(pregunta_info, user_choice):
    _, opciones, respuesta_correcta = pregunta_info
    letras = ['a', 'b', 'c', 'd']
    try:
        opcion_seleccionada = opciones[letras.index(user_choice)].strip().lower()
        return respuesta_correcta == opcion_seleccionada
    except (IndexError, ValueError):
        return False

# Función para manejar una ronda de preguntas
def playRound(trivia, categoria, num_preguntas=10, username="", usuarios={}):
    preguntas = trivia[categoria]
    correctas = 0
    # Mezclamos las preguntas para que el orden varíe en cada ronda.
    preguntas = preguntas[:num_preguntas]
    
    for pregunta_info in preguntas:
        askQuestion(pregunta_info)
        user_choice = input("Elige una opción (a-d): ").lower()
        if checkAnswer(pregunta_info, user_choice):
            print("¡Correcto!")
            correctas += 1
        else:
            print("Respuesta incorrecta.")
    
    # Actualizar las respuestas correctas del usuario
    usuarios[username]['correctas'] += correctas
    saveUsers(usuarios)
    print(f"\nHas respondido correctamente {correctas} preguntas en esta ronda.")
    print(f"Total de preguntas correctas de {username}: {usuarios[username]['correctas']}")

# Función para ver usuarios conectados
def verUsuariosConectados():
    print("\n---Usuarios Conectados---")
    if usuarios_conectados:
        for user in usuarios_conectados:
            print(user)
    else:
        print("No hay usuarios conectados.")

# Función para cerrar sesión
def logout(username, usuarios):
    if username in usuarios_conectados:
        usuarios_conectados.remove(username)
        usuarios[username]['conectado'] = "desconectado"  # Marcar como desconectado
        saveUsers(usuarios)
        print(f"{username} ha cerrado sesión.")
    else:
        print(f"{username} no está conectado.")

# Función principal del juego trivia
def triviaGame():
    trivia = loadTrivia()
    usuarios = loadUsers()
    username = None  # Ningún usuario está conectado al principio

    while True:
        print("\nOpciones:")
        print("1. Iniciar sesión")
        print("2. Registrar nuevo usuario")
        print("3. Ver usuarios conectados")
        print("4. Jugar trivia")
        print("5. Cerrar sesión")
        print("6. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == '1':
            # Iniciar sesión
            username, usuarios = loginUser(usuarios)
            if username:
                # Si el usuario inicia sesión, pasa directamente a jugar
                categorias = list(trivia.keys())
                print("\nElige una categoría:")
                for i, cat in enumerate(categorias):
                    print(f"{i+1}. {cat}")

                try:
                    categoria_index = int(input("Introduce el número de la categoría: ")) - 1
                    if 0 <= categoria_index < len(categorias):
                        categoria = categorias[categoria_index]
                        playRound(trivia, categoria, username=username, usuarios=usuarios)
                    else:
                        print("Número de categoría inválido")
                except ValueError:
                    print("Entrada no válida")

        elif opcion == '2':
            # Registrar nuevo usuario
            username, usuarios = registerUser(usuarios)
            if username:
                # Si el usuario se registra, pasa directamente a jugar
                categorias = list(trivia.keys())
                print("\nElige una categoría:")
                for i, cat in enumerate(categorias):
                    print(f"{i+1}. {cat}")

                try:
                    categoria_index = int(input("Introduce el número de la categoría: ")) - 1
                    if 0 <= categoria_index < len(categorias):
                        categoria = categorias[categoria_index]
                        playRound(trivia, categoria, username=username, usuarios=usuarios)
                    else:
                        print("Número de categoría inválido")
                except ValueError:
                    print("Entrada no válida")

        elif opcion == '3':
            # Ver usuarios conectados
            verUsuariosConectados()

        elif opcion == '4':
            if username:
                categorias = list(trivia.keys())
                print("\nElige una categoría:")
                for i, cat in enumerate(categorias):
                    print(f"{i+1}. {cat}")

                try:
                    categoria_index = int(input("Introduce el número de la categoría: ")) - 1
                    if 0 <= categoria_index < len(categorias):
                        categoria = categorias[categoria_index]
                        playRound(trivia, categoria, username=username, usuarios=usuarios)
                    else:
                        print("Número de categoría inválido")
                except ValueError:
                    print("Entrada no válida")
            else:
                print("Primero debes iniciar sesión o registrarte.")

        elif opcion == '5':
            # Cerrar sesión
            if username:
                logout(username, usuarios)
                username = None
            else:
                print("No has iniciado sesión.")

        elif opcion == '6':
            print("¡Gracias por jugar!")
            break
        else:
            print("Opción no válida, por favor selecciona de nuevo.")

# Ejecutar el trivia
triviaGame()