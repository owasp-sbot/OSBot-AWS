import functools
from typing import get_type_hints, Union, Any


def enforce_type_safety(func):
    @functools.wraps(func)                                                                         # Preserve function's metadata during wrapping
    def wrapper(*args, **kwargs):                                                                  # Define the wrapper function to add type safety

        hints    = get_type_hints(func)                                                            # Retrieve type annotations of the function
        all_args = kwargs.copy()                                                                   # Start with keyword arguments
        all_args.update(dict(zip(func.__code__.co_varnames, args)))                                # Add positional arguments to the same dictionary

        for var_name, var_type in all_args.items():                                                # Iterate over all arguments provided to the function
            if var_name in hints:                                                                  # Check if the argument has a type hint specified
                expected_type = hints[var_name]                                                    # Get the expected type from type hints
                if expected_type is Any or expected_type is any:                                   # Skip type checking for Any, as it accepts any type
                    continue
                if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:     # Check if the type hint is a Union
                    expected_types = expected_type.__args__                                        # Retrieve all types inside the Union
                else:
                    expected_types = (expected_type,)                                              # Wrap the expected type in a tuple for consistency

                if not isinstance(var_type, expected_types):                                       # Validate the type of the current argument
                    type_names    = ', '.join([t.__name__ for t in expected_types])                # Format the names of the expected types for the error message
                    error_message = (f"in '{func.__name__}' the '{var_name}' parameter "
                                     f"must be an '{type_names}', "
                                     f"but it was an '{type(var_type).__name__}'")                 # Construct the error message
                    raise TypeError(error_message)                                                 # Raise TypeError if the argument type does not match

        return func(*args, **kwargs)                                                               # Call the original function with the validated arguments
    return wrapper                                                                                 # Return the wrapped function
