# 🚀 Task Manager (Decoupled Python Architecture)
This project implements a basic task management system (To-Do List) in Python, with a focus on clean architecture, strict testability, and clear separation of responsibilities. It serves as a solid demonstration of professional design patterns applied to a common application.
## ✨ Application Features
- Full CRUD: Create, read (list pending tasks, search by ID), update (mark as completed), and delete tasks.
- Due Date Management: Includes due dates and complex filtering logic to identify overdue tasks.
- Persistence: Uses SQLite as the persistence backend.
## 🏗️ Architectural Highlights
The code structure is designed for scalability and maintainability:
1. Repository Pattern
   The business layer (`TaskManager`) is fully isolated from the database technology (`TaskRepository`). This means you could swap SQLite for any other technology (Postgres, Mock DB) without changing a single line of business logic.
2. Dependency Injection (DI)
   `TaskManager` receives its dependencies (the repository and the clock) through its constructor. This makes components easier to decouple and replace.
3. Deterministic Testability (Clock Injection)
   Time-dependent logic, such as determining whether a task is overdue, is tested by injecting a `MockClock` object. This ensures all time-based tests are 100% predictable and do not fail randomly due to the passage of real time.
## 📁 Project Structure
- `src/task_manager.py`: Business logic layer.
- `src/task_repository.py`: Persistence layer (contains SQL, connection handling, and type mapping).
- `src/clock_interface.py`: Defines the contract (`AbstractClock`).
- `src/clock_implementations.py`: Contains `SystemClock` and `MockClock` for testing.
- `tests/`: Contains rigorous unit tests written following TDD principles.
## 🛠️ Getting Started
Clone the repository:
```bash
git clone [your-repo-link]
cd [your-repo-name]
Run tests (recommended):
python -m unittest
> Note: python -m unittest is assumed to run all tests inside your tests/ folder.
