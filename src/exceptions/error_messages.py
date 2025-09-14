"""Centralized error messages for VRP API."""


class ErrorMessage:
    
    INTERNAL_ERROR = "An internal error occurred. Please try again later."
    VALIDATION_ERROR = "Input validation failed: {details}"
    SOLVER_ERROR = "Solver error: {details}"
    TIMEOUT_ERROR = "Operation timed out after {timeout_seconds} seconds."
    DATABASE_ERROR = "Database operation failed: {details}"
    SOLUTION_ERROR = "Solution processing failed: {details}"