"""Centralized error messages for VRP API."""


class ErrorMessage:
    
    INTERNAL_ERROR = "An internal error occurred. Please try again later."
    VALIDATION_ERROR = "Validation error in input data."
    
    VRP_ERROR = "Error occurred during VRP solution."
    SOLVER_ERROR = "Error occurred in solver algorithm."
    TIMEOUT_ERROR = "Solver timed out."
    
    INVALID_VEHICLE_DATA = "Error in vehicle data: {details}"
    INVALID_JOB_DATA = "Error in job data: {details}"
    INVALID_MATRIX_DATA = "Error in distance matrix data: {details}"
    CAPACITY_EXCEEDED = "Vehicle capacity exceeded: {vehicle_id}"
    INVALID_LOCATION_INDEX = "Invalid location index: {index}"
    
    DATABASE_CONNECTION_ERROR = "Database connection could not be established: {details}"
    DATABASE_SAVE_ERROR = "Database save error: {details}"
    DATABASE_QUERY_ERROR = "Database query error: {details}"
    
    NO_SOLUTION_FOUND = "OR-Tools solver could not find a solution."
    SOLVER_INITIALIZATION_ERROR = "Solver could not be initialized: {details}"
    ROUTE_VALIDATION_ERROR = "Route validation error: {details}"
    INVALID_ROUTE_ASSIGNMENT = "Invalid route assignment: {details}"
    
    SOLUTION_VALIDATION_ERROR = "Solution validation failed: {details}"