class LLMInvocationError(Exception):
    """
    Custom exception for errors occurring during LLM invocation.
    """
    def __init__(self, error_code: int, message: str, original_exception: Exception = None):
        self.error_code = error_code
        self.message = message
        self.original_exception = original_exception
        super().__init__(f"[{error_code}] {message}")
