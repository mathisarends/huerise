---
name: python-ddd-architecture
description: >
  Folder structure, dependency rules, and conventions for adding features to this project.
  Use this when asked to add a feature, create a new domain, add a command, query, or handler,
  or when navigating the project structure.
---

# Project Architecture

This project follows **Domain-Driven Design** with a strict layered architecture per domain. Each domain is a vertical slice and fully self-contained.

## Folder Structure

```
src/
└── <domain>/
    ├── application/
    │   ├── __init__.py          ← re-exports everything public
    │   ├── commands/
    │   │   ├── __init__.py
    │   │   └── create_user.py   ← one file per command
    │   ├── queries/
    │   │   ├── __init__.py
    │   │   └── get_user.py      ← one file per query
    │   └── exceptions.py
    ├── domain/
    │   ├── __init__.py
    │   ├── aggregate.py
    │   ├── exceptions.py
    │   ├── ports.py             ← abstract repository interfaces only
    │   └── value_objects.py
    ├── infrastructure/
    │   ├── di/
    │   │   └── container.py     ← Dishka provider for this domain
    │   ├── persistence/
    │   │   ├── orm.py           ← SQLAlchemy models
    │   │   └── repository.py    ← implements ports.py
    │   └── adapters/            ← external services (email, S3, etc.)
    └── presentation/
        ├── router.py
        ├── schemas.py           ← Pydantic request/response DTOs
        └── exception_handlers.py
```

## Dependency Rule

Dependencies only point inward — never outward:

```
presentation → application → domain ← infrastructure
```

- `domain/` has zero framework imports — pure Python only
- `application/` imports from `domain/` only — no FastAPI, no SQLAlchemy
- `infrastructure/` imports from `domain/` to implement its ports
- `presentation/` imports from `application/` only — never from `domain/` or `infrastructure/` directly

Domains never import from each other. Cross-domain communication goes via domain events or a shared kernel.

## Commands & Queries

Defined as frozen dataclasses — one per file:

```python
# application/commands/create_user.py
from dataclasses import dataclass

@dataclass(frozen=True)
class CreateUserCommand:
    name: str
    email: str
    password: str
```

## Command & Query Handlers

Plain classes. Dependencies injected via `__init__`, stored with a leading underscore. The only public method is `execute`:

```python
class CreateUserCommandHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, command: CreateUserCommand) -> User:
        # ...
        return user
```

Raise domain-specific exceptions — never HTTP exceptions inside handlers.

## Re-exports via `__init__.py`

Every `application/` package exposes a single public surface via its `__init__.py`. Consumers import only from the package, never from submodules directly:

```python
# application/__init__.py
from .commands.create_user import CreateUserCommand, CreateUserCommandHandler
from .commands.delete_user import DeleteUserCommand, DeleteUserCommandHandler
from .queries.get_user import GetUserQuery, GetUserQueryHandler
from .exceptions import UserNotFoundException

__all__ = [
    "CreateUserCommand",
    "CreateUserCommandHandler",
    "DeleteUserCommand",
    "DeleteUserCommandHandler",
    "GetUserQuery",
    "GetUserQueryHandler",
    "UserNotFoundException",
]
```

Consumers then import like:

```python
from domains.user.application import CreateUserCommand, CreateUserCommandHandler
```

The same pattern applies to `domain/` and `infrastructure/di/` — each layer exposes only what the next layer needs.

## Presentation Layer

Use `DishkaRoute` for dependency injection. Inject handlers via `FromDishka[HandlerType]`. Map domain objects to response schemas in a private `_to_*_response` helper at the bottom of the file — never let domain models leak into the response directly:

```python
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])

@router.post("/")
async def create_user(
    body: CreateUserRequest,
    handler: FromDishka[CreateUserCommandHandler],
) -> UserResponse:
    user = await handler.execute(CreateUserCommand(**body.model_dump()))
    return _to_user_response(user)

def _to_user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, name=user.name, email=user.email)
```

Domain exceptions are mapped to HTTP responses in `exception_handlers.py` — never inside the handler or the route function.

## General Conventions

- Use `X | None` instead of `Optional[X]`
- One command or query per file
- Generate IDs with `uuid4()` at the application layer — not in the domain model constructor
- No mutable default arguments
