from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Any
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T], ABC):
    """Base repository interface defining common operations."""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get an entity by its ID."""
        pass
    
    @abstractmethod
    def get_all(self, *args, **kwargs) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity by its ID."""
        pass
    
    @abstractmethod
    def filter(self, **kwargs) -> List[T]:
        """Filter entities by given criteria."""
        pass 