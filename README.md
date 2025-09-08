# MyIdeaCopilot Backend - Phase 1

A FastAPI-based backend for MyIdeaCopilot, focusing on user management and settings functionality.

## Features

- **User Authentication**: Email/password and magic link authentication via Supabase
- **User Profiles**: Complete profile management with validation
- **User Settings**: Flexible key-value settings system
- **User Statistics**: Basic user stats tracking
- **JWT Authentication**: Secure API endpoints with middleware
- **Row Level Security**: Database-level security via Supabase RLS

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Supabase** - Backend-as-a-service with PostgreSQL, Auth, and RLS
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server for FastAPI

## Project Structure