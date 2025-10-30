# errors_mapping.py
"""
Contains CATEGORY_MAPPING and helper functions to flatten / query the mapping.
This file holds the full list of categories and sub-errors.
"""

from typing import Dict, List

CATEGORY_MAPPING: Dict[str, Dict] = {
    "Type_1_Syntax": {
        "category": "Syntax and Parsing Errors",
        "description": "Errors that occur during parsing of Python code before execution.",
        "errors": [
            "SyntaxError", "IndentationError", "TabError", "SyntaxWarning"
        ]
    },
    "Type_2_Runtime": {
        "category": "Runtime and Logical Errors",
        "description": "Errors that occur during runtime of valid Python code.",
        "errors": [
            "Exception", "BaseException", "ArithmeticError", "AssertionError", "AttributeError", "BufferError",
            "EOFError", "FloatingPointError", "GeneratorExit", "ImportError", "ModuleNotFoundError", "IndexError",
            "KeyError", "KeyboardInterrupt", "MemoryError", "NameError", "NotImplementedError", "OSError",
            "OverflowError", "RecursionError", "ReferenceError", "RuntimeError", "StopIteration", "StopAsyncIteration",
            "SyntaxError", "SystemError", "SystemExit", "TypeError", "ValueError", "ZeroDivisionError",
            "LookupError", "UnboundLocalError", "TimeoutError", "BlockingIOError", "BrokenPipeError",
            "ChildProcessError", "ConnectionError", "PermissionError", "ProcessLookupError", "FileNotFoundError",
            "FileExistsError", "IsADirectoryError", "NotADirectoryError", "InterruptedError"
        ]
    },
    "Type_3_Import": {
        "category": "Import and Module Errors",
        "description": "Errors related to imports and package availability.",
        "errors": [
            "ImportError", "ModuleNotFoundError", "PackageNotFoundError", "ZipImportError"
        ]
    },
    "Type_4_IO_OS": {
        "category": "I/O and Operating System Errors",
        "description": "File/OS and I/O errors.",
        "errors": [
            "OSError", "IOError", "FileNotFoundError", "PermissionError", "FileExistsError", "IsADirectoryError",
            "NotADirectoryError", "BlockingIOError", "ChildProcessError", "BrokenPipeError", "InterruptedError",
            "ProcessLookupError", "TimeoutError", "UnsupportedOperation", "EOFError"
        ]
    },
    "Type_5_Network": {
        "category": "Network and AsyncIO Errors",
        "description": "Networking, sockets, and asyncio errors.",
        "errors": [
            "ConnectionError", "ConnectionAbortedError", "ConnectionRefusedError", "ConnectionResetError",
            "socket.gaierror", "socket.herror", "socket.timeout", "ssl.SSLError",
            "asyncio.TimeoutError", "asyncio.CancelledError", "asyncio.InvalidStateError",
            "asyncio.IncompleteReadError", "asyncio.LimitOverrunError",
            "requests.exceptions.RequestException", "requests.exceptions.Timeout",
            "requests.exceptions.ConnectionError", "http.client.HTTPException"
        ]
    },
    "Type_6_Concurrency": {
        "category": "Threading and Multiprocessing Errors",
        "description": "Errors from threading, multiprocessing and concurrency libs.",
        "errors": [
            "threading.ThreadError", "concurrent.futures.TimeoutError", "BrokenProcessPool",
            "multiprocessing.ProcessError", "multiprocessing.AuthenticationError", "multiprocessing.BufferTooShort",
            "RuntimeError", "DeadlockError"
        ]
    },
    "Type_7_System": {
        "category": "System Exit and Signal Errors",
        "description": "Process exit and signals.",
        "errors": [
            "SystemExit", "KeyboardInterrupt", "GeneratorExit"
        ]
    },
    "Type_8_Arithmetic": {
        "category": "Arithmetic and Numeric Errors",
        "description": "Numeric / math related errors.",
        "errors": [
            "ArithmeticError", "FloatingPointError", "OverflowError", "ZeroDivisionError",
            "numpy.linalg.LinAlgError", "numpy.AxisError", "decimal.InvalidOperation"
        ]
    },
    "Type_9_Database": {
        "category": "Database and ORM Errors",
        "description": "Database drivers and ORM errors.",
        "errors": [
            "DatabaseError", "InterfaceError", "OperationalError", "IntegrityError", "DataError",
            "ProgrammingError", "InternalError", "NotSupportedError",
            "psycopg2.Error", "psycopg2.OperationalError", "psycopg2.IntegrityError",
            "sqlite3.Error", "sqlite3.OperationalError", "pymongo.errors.PyMongoError",
            "django.db.IntegrityError", "django.core.exceptions.ObjectDoesNotExist",
            "sqlalchemy.exc.IntegrityError", "sqlalchemy.exc.OperationalError"
        ]
    },
    "Type_10_Serialization": {
        "category": "Serialization and Data Parsing Errors",
        "description": "JSON/YAML/XML parsing and serialization errors.",
        "errors": [
            "json.JSONDecodeError", "pickle.PickleError", "pickle.UnpicklingError", "pickle.PicklingError",
            "yaml.YAMLError", "xml.etree.ElementTree.ParseError", "csv.Error", "configparser.Error",
            "msgpack.ExtraData"
        ]
    },
    "Type_11_Warnings": {
        "category": "Warnings (Non-fatal Issues)",
        "description": "Warning classes (non-fatal).",
        "errors": [
            "Warning", "UserWarning", "DeprecationWarning", "PendingDeprecationWarning", "SyntaxWarning",
            "RuntimeWarning", "FutureWarning", "ImportWarning", "UnicodeWarning", "BytesWarning", "ResourceWarning"
        ]
    },
    "Type_12_Unicode": {
        "category": "Unicode and Encoding Errors",
        "description": "Encoding/decoding and unicode problems.",
        "errors": [
            "UnicodeError", "UnicodeEncodeError", "UnicodeDecodeError", "UnicodeTranslateError"
        ]
    },
    "Type_13_Security": {
        "category": "Security and Cryptography Errors",
        "description": "SSL/TLS, cryptography, JWT, and auth errors.",
        "errors": [
            "ssl.SSLError", "cryptography.exceptions.InvalidSignature", "cryptography.exceptions.InvalidKey",
            "jwt.exceptions.ExpiredSignatureError", "jwt.exceptions.InvalidTokenError", "PermissionError",
            "paramiko.ssh_exception.SSHException"
        ]
    },
    "Type_14_HTTP_API": {
        "category": "HTTP and API Client Errors",
        "description": "HTTP client & framework errors (requests, starlette, fastapi, werkzeug).",
        "errors": [
            "requests.exceptions.Timeout", "requests.exceptions.ConnectionError", "requests.exceptions.SSLError",
            "requests.exceptions.TooManyRedirects", "http.client.HTTPException",
            "starlette.exceptions.HTTPException", "fastapi.exceptions.RequestValidationError",
            "werkzeug.exceptions.BadRequest", "werkzeug.exceptions.NotFound", "werkzeug.exceptions.InternalServerError",
            "aiohttp.ClientError", "aiohttp.ClientConnectorError"
        ]
    },
    "Type_15_Custom": {
        "category": "Custom and Framework-Specific Errors",
        "description": "Application-specific or third-party custom error classes.",
        "errors": [
            "MyAppError", "CustomError", "ValidationError", "AuthenticationError", "AuthorizationError",
            "RateLimitError", "ServiceUnavailableError", "ThirdPartyAPIError",
            "django.core.exceptions.ValidationError", "flask_restful.errors.BadRequest"
        ]
    },
    "Type_99_Others": {
        "category": "Other/Additional Exceptions",
        "description": "Misc builtins and library exceptions included for completeness.",
        "errors": [
            "BaseException", "Exception", "EnvironmentError", "WindowsError",
            "ImportWarning", "ResourceWarning", "StopIteration", "StopAsyncIteration",
            "MemoryError", "BufferError", "LookupError", "IndexError", "KeyError", "OSError",
            "ModuleNotFoundError", "ImportError", "AttributeError", "NameError", "ReferenceError",
            "RecursionError", "NotImplementedError", "SystemError", "SystemExit",
            "pandas.errors.EmptyDataError", "pandas.errors.ParserError", "numpy.AxisError",
            "sklearn.exceptions.NotFittedError", "tensorflow.errors.OpError",
            "concurrent.futures.TimeoutError", "asyncio.CancelledError"
        ]
    }
}

# Flatten mapping: sub-error -> category key
SUB_TO_CAT = {}
for cat_key, cat_obj in CATEGORY_MAPPING.items():
    for sub in cat_obj["errors"]:
        if sub not in SUB_TO_CAT:
            SUB_TO_CAT[sub] = cat_key


def get_all_suberrors() -> List[str]:
    """Return sorted list of all sub-error names in the mapping."""
    subs = sorted({s for cat in CATEGORY_MAPPING.values() for s in cat["errors"]})
    return subs


def find_category_for_suberror(sub: str):
    """Return category key if sub exists, else None."""
    return SUB_TO_CAT.get(sub)
