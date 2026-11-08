# LifeOS Task Management Architecture

## 1. Executive Summary & Design Principles

The **Smart Task Management System** is a foundational execution domain of LifeOS. It manages the complete lifecycle of daily to-dos, priorities, deadlines, and project milestones across both the Flask REST API and the React Native client.

### Key Architectural Tenets
- **Strict User Isolation**: All task queries enforce `user_id == current_user_id` derived exclusively from cryptographically verified JWT tokens. Cross-user IDOR access is strictly rejected with HTTP 403.
- **Layered Backend Architecture**: Clear separation between API Blueprints (`routes.py`), Validation (`schemas/task.py`), Business Logic (`services/task_service.py`), and Data Access (`repositories/task_repository.py`).
- **N+1 Prevention**: Category relationships are eager-loaded with SQLAlchemy `joinedload(Task.category)`.
- **Reactive Cache Synchronization**: TanStack Query mutations (`useCreateTask`, `useUpdateTask`, `useToggleCompleteTask`, `useDeleteTask`) invalidate both task queries (`['tasks']`) and dashboard queries (`['dashboardOverview']`), ensuring real-time UI synchronization without page reloads.

---

## 2. Component Hierarchy & Navigation

```
MainTabNavigator (Bottom Tab Bar)
└── TasksTab (TasksScreen)
    ├── Screen Header ("Tasks", total task count badge, "+ New Task" button)
    ├── SearchInput (debounced query filter)
    ├── Status Filter Chips (All, Pending, In Progress, Completed)
    ├── Priority Filter Chips (All, Urgent, High, Medium, Low)
    ├── Task List (FlatList / ScrollContainer)
    │   ├── SkeletonLoader (during fetch)
    │   ├── ErrorState (with retry on failure)
    │   ├── EmptyState (when zero tasks match active filters)
    │   └── Task Item Cards
    │       ├── Color-coded Priority Strip (urgent, high, medium, low)
    │       ├── Interactive Checkbox (1-tap complete / uncomplete toggle)
    │       ├── Title & Category Tag Chip
    │       └── Due Date indicator
    ├── CreateEditTaskModal
    │   ├── Title (validated required input)
    │   ├── Description (multiline glass input)
    │   ├── Priority selector chips (Low, Medium, High, Urgent)
    │   ├── Category selector chips (loaded from useTaskCategories)
    │   └── Due Date quick buttons (Today, Tomorrow, Next Week, Clear)
    └── TaskDetailsModal
        ├── Title, Priority badge, Category chip, Status badge
        ├── Description scroll view
        ├── Date metadata (Due date, Completed at, Created at)
        ├── "Mark Completed" / "Reopen" PrimaryButton
        ├── "Edit Task" SecondaryButton
        └── "Delete" Action (with ConfirmationModal)
```

---

## 3. End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant View as TasksScreen
    participant Hook as useToggleCompleteTask
    participant Client as taskService (Axios)
    participant Route as tasks_bp (Flask)
    participant Service as TaskService
    participant Repo as TaskRepository
    participant DB as PostgreSQL

    User->>View: Taps task completion circle
    View->>Hook: mutate(taskId)
    Hook->>Client: PATCH /api/v1/tasks/:id/complete
    Client->>Route: HTTP PATCH with Bearer JWT
    Route->>Service: toggle_complete_task(task_id, current_user_id)
    Service->>Repo: get_by_id(task_id)
    Repo->>DB: SELECT * FROM tasks WHERE id = :id
    DB-->>Repo: Task entity
    Repo-->>Service: Task entity
    Service->>Service: check_resource_ownership(task.user_id, current_user_id)
    Service->>Repo: update(task, status="completed", completed_at=now())
    Repo->>DB: UPDATE tasks SET status = 'completed', completed_at = :now
    DB-->>Repo: Success
    Repo-->>Service: Updated Task
    Service-->>Route: Updated Task
    Route-->>Client: 200 OK (Task payload)
    Client-->>Hook: Success
    Hook->>View: Invalidates ['tasks'] & ['dashboardOverview']
    Note over View: Dashboard and Task List update simultaneously
```

