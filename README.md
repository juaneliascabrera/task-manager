# 🚀 Task Manager (Decoupled Python Architecture)

Este proyecto implementa un sistema de gestión de tareas (To-Do List) básico en Python, con un enfoque en la **arquitectura limpia**, la **testabilidad rigurosa** y la **separación de responsabilidades**. Sirve como una demostración sólida de patrones de diseño profesionales aplicados a una aplicación común.

## ✨ Características de la Aplicación

* **CRUD Completo:** Permite crear, leer (listar pendientes, buscar por ID), actualizar (marcar como completada) y eliminar tareas.
* **Gestión de Plazos:** Incluye el concepto de fechas de vencimiento (`due_date`) y lógica de filtrado compleja para identificar tareas **Vencidas (`Overdue`)**.
* **Persistencia:** Utiliza **SQLite** como el *backend* de persistencia.

## 🏗️ Highlights Arquitectónicos

La estructura del código está diseñada para la escalabilidad y el mantenimiento:

### 1. Patrón Repositorio
La capa de negocio (`TaskManager`) está completamente aislada de la tecnología de base de datos (`TaskRepository`). Esto significa que podrías cambiar SQLite por cualquier otra tecnología (Postgres, Mock DB) sin modificar una sola línea de la lógica de negocio. 

### 2. Inyección de Dependencias (DI)
El `TaskManager` recibe sus dependencias (el Repositorio y el Reloj) en su constructor. Esto facilita el **desacoplamiento** y la **sustitución** de componentes.

### 3. Testabilidad Determinista (Clock Injection)
La lógica dependiente del tiempo (como la determinación de tareas vencidas) se prueba inyectando un objeto `MockClock`. Esto garantiza que todos los tests de tiempo sean **100% predecibles** y no fallen aleatoriamente debido al paso del tiempo real.

## 📁 Estructura del Proyecto

* `src/task_manager.py`: La Capa de Lógica de Negocio.
* `src/task_repository.py`: La Capa de Persistencia (contiene SQL, manejo de la conexión y el mapeo de tipos).
* `src/clock_interface.py`: Define el contrato (`AbstractClock`).
* `src/clock_implementations.py`: Contiene el `SystemClock` y el `MockClock` para el testing.
* `tests/`: Contiene los *unit tests* rigurosos escritos siguiendo la filosofía TDD.

## 🛠️ Cómo Empezar

1.  **Clonar el Repositorio:**
    ```bash
    git clone [tu-link-al-repo]
    cd [nombre-de-tu-repo]
    ```
2.  **Ejecutar Tests (Recomendado):**
    ```bash
    python -m unittest
    ```

**(Nota: El comando `python -m unittest` se asume que ejecutará todos los tests dentro de tu carpeta `tests/`).**