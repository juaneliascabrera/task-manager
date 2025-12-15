# app.py

import os
import sys
from datetime import datetime, timedelta
# Importamos las clases clave de tu proyecto
from src.task_manager import TaskManager, AuthenticationError, UsernameAlreadyExistsError, TaskNotFoundError
from src.task_repository import TaskRepository
from src.clock_implementations import SystemClock # Usamos el reloj real para una app real
from src.cli_facade import TaskManagerCliFacade

# -- CONFIGURACIÓN GLOBAL --
DB_NAME = 'elias_taskmanager.db'

def setup_application():
    """Configura e inyecta todas las dependencias (Inyección de Dependencias)."""
    
    # Dependencias de Infraestructura
    clock = SystemClock()
    # Conecta a la DB real (memory=False)
    repository = TaskRepository(DB_NAME, clock, memory=False) 

    # Capa de Dominio
    manager = TaskManager(repository)

    # Capa de Aplicación/Interfaz
    facade = TaskManagerCliFacade(manager)
    
    return facade, repository

def display_menu(username):
    """Muestra el menú principal de la sesión."""
    print("\n--- MENÚ PRINCIPAL ---")
    print(f"Sesión activa: **{username}**")
    print("1. 📝 Crear nueva tarea")
    print("2. 📋 Ver mis tareas pendientes")
    print("3. ✅ Completar una tarea")
    print("4. 🗑️ Borrar una tarea")
    print("5. 🔄 Modificar descripción/fecha de una tarea")
    print("6. 🚪 Cambiar de usuario / Salir")
    return input("Elige una opción (1-6): ")

def handle_create_task(facade, username):
    """Maneja la creación de una nueva tarea."""
    print("\n--- Crear Nueva Tarea ---")
    description = input("Descripción de la tarea: ")
    due_date_str = input("Fecha de vencimiento (YYYY-MM-DD HH:MM:SS) [Opcional, dejar vacío]: ")
    
    due_date = None
    if due_date_str:
        try:
            # Intentamos parsear la fecha ingresada
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("❌ Formato de fecha y hora inválido. Tarea creada sin fecha de vencimiento.")

    try:
        task_id = facade.create_task(username, description, due_date)
        print(f"✅ Tarea creada con ID: {task_id}")
    except Exception as e:
        print(f"❌ Error al crear tarea: {e}")

def handle_list_pending_tasks(facade, username):
    """Maneja el listado de tareas pendientes."""
    print(f"\n--- Tareas Pendientes de {username} ---")
    try:
        # Aquí la Fachada impone la regla de que solo ves tus tareas
        tasks = facade.list_pending_tasks(username)
        
        if not tasks:
            print("🎉 ¡No tienes tareas pendientes! Estás al día.")
            return

        for task in tasks:
            due_date = task.get_due_date().strftime('%Y-%m-%d') if task.get_due_date() else 'N/A'
            print(f"[ID: {task.get_id()}] | Vence: {due_date} | Descripción: {task.get_description()}")
            
    except Exception as e:
        print(f"❌ Error al listar tareas: {e}")

def handle_complete_task(facade, username):
    """Maneja el completado de una tarea."""
    task_id_str = input("ID de la tarea a completar: ")
    try:
        task_id = int(task_id_str)
        # La Fachada usa el username para validar la pertenencia antes de completar
        facade.complete_task(username, task_id)
        print(f"✅ Tarea {task_id} marcada como completada.")
    except ValueError:
        print("❌ ID de tarea inválido.")
    except (AuthenticationError, TaskNotFoundError) as e:
        print(f"❌ ERROR: {e}. Asegúrate de que el ID es correcto y la tarea te pertenece.")
    except Exception as e:
        print(f"❌ Error desconocido: {e}")

def handle_delete_task(facade, username):
    """Maneja la eliminación de una tarea."""
    task_id_str = input("ID de la tarea a borrar: ")
    try:
        task_id = int(task_id_str)
        # La Fachada usa el username para validar la pertenencia antes de borrar
        facade.delete_task(username, task_id)
        print(f"✅ Tarea {task_id} eliminada.")
    except ValueError:
        print("❌ ID de tarea inválido.")
    except (AuthenticationError, TaskNotFoundError) as e:
        print(f"❌ ERROR: {e}. Asegúrate de que el ID es correcto y la tarea te pertenece.")
    except Exception as e:
        print(f"❌ Error desconocido: {e}")

def handle_modify_task(facade, username):
    """Maneja la modificación de descripción o fecha."""
    print("\n--- Modificar Tarea ---")
    task_id_str = input("ID de la tarea a modificar: ")
    try:
        task_id = int(task_id_str)
        
        print("¿Qué desea modificar?")
        print("1. Descripción")
        print("2. Fecha de vencimiento")
        choice = input("Elige una opción (1 o 2): ")
        
        if choice == '1':
            new_desc = input("Nueva descripción: ")
            facade.update_task_description(username, task_id, new_desc)
            print("✅ Descripción actualizada.")
        elif choice == '2':
            new_date_str = input("Nueva fecha (YYYY-MM-DD HH:MM:SS): ")
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d %H:%M:%S')
            facade.update_task_date(username, task_id, new_date)
            print("✅ Fecha actualizada.")
        else:
            print("❌ Opción inválida.")
            
    except ValueError:
        print("❌ ID o formato de fecha/hora inválido.")
    except (AuthenticationError, TaskNotFoundError) as e:
        print(f"❌ ERROR: {e}. Asegúrate de que el ID es correcto y la tarea te pertenece.")
    except Exception as e:
        print(f"❌ Error desconocido: {e}")


def handle_login_and_main_loop(facade):
    """Maneja el inicio de sesión o registro y el bucle principal de la CLI."""
    current_user = None
    
    while True:
        if current_user is None:
            # -- LOGIN / REGISTRO --
            print("\n--- GESTOR DE TAREAS ---")
            print("1. 👤 Iniciar Sesión (Ingresar tu nombre)")
            print("2. 🆕 Registrar nuevo usuario")
            print("3. ❌ Salir de la aplicación")
            
            choice = input("Elige una opción (1-3): ")
            
            if choice == '3':
                print("¡Gracias por usar el Gestor de Tareas! Adiós.")
                return

            username = input("Ingresa tu nombre de usuario: ")
            
            if choice == '1':
                try:
                    # Intenta obtener el ID; si falla, el usuario no existe.
                    facade.manager.get_user_id_by_username(username)
                    current_user = username
                    print(f"🎉 Bienvenido de nuevo, {current_user}.")
                except AuthenticationError:
                    print(f"❌ Error: El usuario '{username}' no existe. Intenta registrarte.")
            
            elif choice == '2':
                try:
                    facade.create_user(username)
                    current_user = username
                    print(f"🎉 Registro exitoso, {current_user}. Sesión iniciada.")
                except UsernameAlreadyExistsError:
                    print(f"❌ Error: El usuario '{username}' ya existe. Por favor, inicia sesión.")
                except Exception as e:
                    print(f"❌ Error en el registro: {e}")
            
            else:
                print("Opción inválida.")
        
        else:
            # -- MENÚ PRINCIPAL DEL USUARIO LOGUEADO --
            action = display_menu(current_user)
            
            if action == '1':
                handle_create_task(facade, current_user)
            elif action == '2':
                handle_list_pending_tasks(facade, current_user)
            elif action == '3':
                handle_complete_task(facade, current_user)
            elif action == '4':
                handle_delete_task(facade, current_user)
            elif action == '5':
                handle_modify_task(facade, current_user)
            elif action == '6':
                current_user = None
                print("Sesión cerrada.")
            else:
                print("Opción inválida. Intenta de nuevo.")


if __name__ == '__main__':
    facade, repo = setup_application()
    try:
        handle_login_and_main_loop(facade)
    finally:
        # Cierra la conexión de la DB al terminar
        repo.close()
        # Nota: Puedes borrar el archivo DB si no quieres persistencia, pero por defecto, lo mantenemos.