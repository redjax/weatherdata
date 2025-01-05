from __future__ import annotations

class UnhandledException(Exception):
    """Exception raised when an unhandled exception occurs.
    
    Attributes:
        message (str): The message to print when the exception is raised.

    """

    def __init__(self, message: str):
        self.message = message
        
        super().__init__(message)
        
    def __str__(self):
        return f"{self.message}"


class FileProcessingError(Exception):
    """Exception raised when an error occurs while processing a file.
    
    Attributes:
        message (str): The message to print when the exception is raised.

    """

    def __init__(self, message: str):
        self.message = message
        
        super().__init__(message)
        
    def __str__(self):
        return f"{self.message}"
    def __init__(self, message, filename, lineno):
        super().__init__(message)
        self.filename = filename
        self.lineno = lineno
        
    def __str__(self):
        return f"{self.message} in {self.filename} on line {self.lineno}"
    

class EntrypointException(Exception):
    """Exception raised when an entrypoint is not a valid entrypoint.
    
    Attributes:
        message (str): The message to print when the exception is raised.

    """
    
    def __init__(self, message: str, file: str, method: str):
        super().__init__(message)
        
        self.file = file
        self.method = method
        
    def __str__(self):
        return f"File '{self.file}' is not a valid entrypoint. Method called: {self.method}. This module is meant to be imported and run from other scripts."
