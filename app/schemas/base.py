from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, Dict, List, TypeVar, Generic

# Type variable for generic model types
T = TypeVar('T')

class CustomBaseModel(BaseModel):
    """
    Base model with common configurations for all Pydantic models.
    """
    model_config = ConfigDict(
        from_attributes=True,  # Replaces orm_mode = True in Pydantic v2
        populate_by_name=True,  # Allow population by field name
        arbitrary_types_allowed=True,
        json_encoders={
            # Add custom JSON encoders here if needed
        }
    )

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        """
        return self.model_dump(**kwargs)

    @classmethod
    def from_orm(cls, obj: Any):
        """
        Convert ORM model to Pydantic model.
        This is a compatibility method for Pydantic v2.
        """
        return cls.model_validate(obj)


class ResponseModel(CustomBaseModel, Generic[T]):
    """
    Standard response model for API responses.
    """
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[List[Dict[str, str]]] = None

    @classmethod
    def success_response(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None
    ) -> 'ResponseModel[T]':
        """
        Create a success response.
        """
        return cls(
            success=True,
            message=message or "Operation completed successfully",
            data=data
        )

    @classmethod
    def error_response(
        cls,
        message: str,
        errors: Optional[List[Dict[str, str]]] = None,
        data: Optional[T] = None
    ) -> 'ResponseModel[T]':
        """
        Create an error response.
        """
        return cls(
            success=False,
            message=message,
            errors=errors or [],
            data=data
        )


class PaginatedResponse(CustomBaseModel, Generic[T]):
    """
    Standard response model for paginated results.
    """
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> 'PaginatedResponse[T]':
        """
        Create a paginated response.
        """
        total_pages = (total + size - 1) // size if size > 0 else 1
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
