from __future__ import annotations

class UnhandledException(Exception):
    def __init__(self, message: str):
        self.message = message
        
        super().__init__(message)
        
    def __str__(self):
        return f"{self.message}"


class FileProcessingError(Exception):
    def __init__(self, message, filename, lineno):
        super().__init__(message)
        self.filename = filename
        self.lineno = lineno
        
    def __str__(self):
        return f"{self.message} in {self.filename} on line {self.lineno}"
    

class EntrypointException(Exception):
    def __init__(self, message: str, file: str, method: str):
        super().__init__(message)
        
        self.file = file
        self.method = method
        
    def __str__(self):
        return f"File '{self.file}' is not a valid entrypoint. Method called: {self.method}. This module is meant to be imported and run from other scripts."
