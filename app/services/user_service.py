from typing import List, Optional, Union, Dict, Any
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.crud.user import (
    get_user,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Service layer for user operations.
    Separates business logic from API endpoints.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, id: int) -> Optional[User]:
        """Get user by ID"""
        return get_user(self.db, id=id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return get_user_by_email(self.db, email=email)
    
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination"""
        return get_users(self.db, skip=skip, limit=limit)
    
    def create(self, *, obj_in: UserCreate) -> User:
        """Create new user"""
        # Here we could add additional business logic like sending welcome emails
        user = create_user(
            db=self.db, 
            obj_in=obj_in
        )
        
        # Additional business logic after user creation
        # TODO: Integrate email functionality by importing the send_welcome_email function
        # from app/utils/email.py and calling it here, e.g.:
        # from app.utils.email import send_welcome_email
        # send_welcome_email(user.email)
        
        return user
    
    def update(
        self, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update existing user"""
        return update_user(self.db, db_obj=db_obj, obj_in=obj_in)
    
    def remove(self, *, id: int) -> User:
        """Remove user"""
        return delete_user(self.db, id=id)
    
    # Placeholder for future email functionality.
    # TODO: Implement this method by integrating the email utilities from app/utils/email.py.
    def _send_welcome_email(self, email: EmailStr) -> None:
        """
        Private method to send welcome email to new users.
        
        It is better to implement email functionality in a dedicated module (app/utils/email.py)
        to keep concerns separated, improve maintainability, and allow for easier testing and
        updates of email features independently of the user service logic.
        """
        
        pass