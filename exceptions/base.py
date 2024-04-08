from typing import Any, Optional, Dict

from fastapi import status



class NotFoundException():

    def __init__(self,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class BadRequestException():

    def __init__(self,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class ForbiddenException():

    def __init__(self,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotSupportedException():

    def __init__(self,
            detail: Any = None,
            headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class InvalidOperationException():

    def __init__(self,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)
