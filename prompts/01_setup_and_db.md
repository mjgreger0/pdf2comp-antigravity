# Task: Phase 1 - Project Setup & Database

## Context
You are the implementation agent for the "MinerU to KiCAD Component Generator" project. Your goal in this phase is to set up the project structure and the SQLite database.

## Resources
- **Architecture**: `doc/architecture.md`
- **Database Schema**: `doc/database_schema.md`
- **Implementation Plan**: `implementation_plan.md`
- **Task List**: `task.md`

## Instructions
1.  **Read the Resources**: Familiarize yourself with the project goals and database design.
2.  **Initialize Project**:
    - Create the directory structure: `src/`, `src/database`, `src/models`, `tests/`, `docker/`.
    - Create `__init__.py` files where necessary.
3.  **Database Implementation**:
    - Create `src/database/schema.sql` with the tables defined in `doc/database_schema.md`.
    - Implement `src/database/db_manager.py`:
        - Class `DBManager`.
        - Methods to initialize the DB, execute queries, and manage connections.
        - Ensure it handles the `correction_log` table correctly.
4.  **Data Models**:
    - Create `src/models/data_models.py` using Pydantic.
    - Define models for `Component`, `Package`, `Pin`, `CorrectionLog`.
5.  **Update Task List**:
    - Mark the corresponding items in `task.md` as completed (`[x]`).

## Deliverables
- `src/database/schema.sql`
- `src/database/db_manager.py`
- `src/models/data_models.py`
- Updated `task.md`
