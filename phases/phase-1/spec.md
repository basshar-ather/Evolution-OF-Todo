# Phase I – Core Todo Backend

## Objective
Implement a basic Todo backend using Spec-Driven Development.

## Todo Entity
- id: UUID
- title: string (required)
- description: string (optional)
- status: pending | completed
- created_at: timestamp
- updated_at: timestamp

## API Endpoints

### Create Todo
POST /todos

### Get Todos
GET /todos

### Update Todo
PUT /todos/{id}

### Delete Todo
DELETE /todos/{id}

## Persistence
- SQLite database
- Data must persist across restarts

## Error Handling
- Invalid input → 400
- Missing Todo → 404

## Acceptance Criteria
- Todos can be created, updated, deleted
- Data persists
- API returns JSON
