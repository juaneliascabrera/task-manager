# 🚀 Task Manager (Decoupled Python Architecture)

This project implements a basic Task Management system (To-Do List) in Python, with a strong focus on clean architecture, rigorous testability, and separation of concerns. It serves as a solid demonstration of professional design patterns applied to a common application.

## ✨ Application Features

- **Full CRUD Support**: Create, read (list pending tasks, retrieve by ID), update (mark as completed), and delete tasks.  
- **Deadline Management**: Supports due dates (`due_date`) and includes logic to filter and identify **overdue** tasks.  
- **Persistence**: Uses SQLite as the storage backend.  

## 🏗️ Architectural Highlights

The codebase is structured for scalability and maintainability:

### 1. Repository Pattern
The business logic layer (`TaskManager`) is completely isolated from the database technology (`TaskRepository`). This allows you to swap SQLite for any other persistence layer (PostgreSQL, mock database, etc.) without modifying a single line of business logic.

### 2. Dependency Injection (DI)
`TaskManager` receives its dependencies (the repository and the clock) through its constructor. This promotes loose coupling and makes components easily replaceable.

### 3. Deterministic Testability (Clock Injection)
Time-dependent logic (such as identifying overdue tasks) is tested by injecting a `MockClock`. This ensures that all time-based tests are fully deterministic and do not fail due to real-time progression.

## 📁 Project Structure

- `src/task_manager.py`: Business Logic Layer  
- `src/task_repository.py`: Persistence Layer (contains SQL, connection handling, and type mapping)  
- `src/clock_interface.py`: Defines the contract (`AbstractClock`)  
- `src/clock_implementations.py`: Contains `SystemClock` and `MockClock` for testing  
- `tests/`: Contains rigorous unit tests written following TDD principles  

## 🛠️ Getting Started

### Clone the Repository
```bash
git clone [your-repo-link]
cd [your-repo-name]
