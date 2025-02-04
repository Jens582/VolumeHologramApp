class RCWAError(Exception):
    
    def __init__(self, message, info):
        super().__init__(message)
        self.info: str = info
        self.message = message
        
class RCWAWrongParameterError(RCWAError):
    def __init__(self, message, info):
        super().__init__(message, info)
        