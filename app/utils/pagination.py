"""Pagination utilities"""
from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    limit: int = 50
    offset: int = 0
    
    @property
    def skip(self) -> int:
        return self.offset
    
    @property
    def take(self) -> int:
        return self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool
    
    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        return cls(
            items=items,
            total=total,
            limit=params.limit,
            offset=params.offset,
            has_more=(params.offset + params.limit) < total
        )


def calculate_pages(total: int, limit: int) -> int:
    """Calculate total number of pages"""
    return (total + limit - 1) // limit


def get_page_info(offset: int, limit: int, total: int) -> dict:
    """Get pagination metadata"""
    current_page = (offset // limit) + 1
    total_pages = calculate_pages(total, limit)
    
    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "has_previous": offset > 0,
        "has_next": (offset + limit) < total,
        "previous_offset": max(0, offset - limit) if offset > 0 else None,
        "next_offset": offset + limit if (offset + limit) < total else None
    }
