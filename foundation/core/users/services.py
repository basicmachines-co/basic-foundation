from typing import Any, Sequence
from uuid import UUID

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from foundation.core.config import settings
from foundation.core.email import (
    generate_new_account_email,
    send_email,
    generate_reset_password_email,
)
from foundation.core.repository import Repository
from foundation.core.security import (
    verify_password,
    get_password_hash,
    generate_password_reset_token,
)
from foundation.core.users.models import User, StatusEnum, RoleEnum


class UserNotFoundError(Exception):
    """
    Exception raised when a user cannot be found by their ID.

    :param id_val: The unique identifier of the user.
    :type id_val: UUID or str

    Example usage:

        try:
            # some code to find the user
            raise UserNotFoundError(user_id)
        except UserNotFoundError as e:
            print(e)

    Raises:
        UserNotFoundError: If the user with the specified ID does not exist.
    """

    def __init__(self, id_val: UUID | str):
        super().__init__(f"The user {id_val} does not exist")


class UserCreateError(Exception):
    """
    Custom exception raised when attempting to create a user that already exists.

    :param email: User email that caused the error
    :type email: str

    Example usage:

        try:
            raise UserCreateError("user@example.com")
        except UserCreateError as e:
            print(e)

    Raises:
        UserCreateError: If a user with the given email already exists
    """

    def __init__(self, email: str):
        super().__init__(f"A user with email {email} already exists")


class UserValueError(Exception):
    """
    Custom exception for handling user value errors.

    This exception is raised when attempting to update a user with an invalid value.

    Example usage:
        >>> raise UserValueError("invalid_email@example.com")
        UserValueError: The user can not be updated with value 'invalid_email@example.com'

    Constructor:
        :param value: The invalid value that triggered the exception.

    Attributes:
        value : Any
            The value that caused this error.

    Errors:
        Raises a formatted exception message including the invalid value.
    """

    def __init__(self, value: Any = None):
        super().__init__(f"The user can not be updated with value '{value}'")


class UserService:
    """
    Handles user-related operations such as creation, updation, deletion, and querying.
    """

    repository: Repository[User]
    current_user: User | None

    def __init__(self, repository: Repository[User], current_user: User | None = None):
        self.repository = repository
        self.current_user = current_user

    async def get_users(self, *, skip: int, limit: int) -> tuple[int, Sequence[User]]:
        """
        Gets a paginated list of users along with the total user count.

        :param skip: Number of users to skip
        :param limit: Maximum number of users to return
        :return: Tuple containing the total user count and a sequence of users
        :raises: DatabaseError if the database query fails
        """
        count = await self.repository.count()
        users = await self.repository.find_all(skip, limit)
        return count, users

    async def get_user_by_id(self, *, user_id: UUID) -> User:
        """
        Fetches user information based on the provided user ID.

        :param user_id: Unique identifier of the user to fetch
        :type user_id: UUID
        :return: User model object corresponding to the provided ID
        :rtype: User
        :raises UserNotFoundError: If no user is found with the given ID
        """
        user = await self.repository.find_by_id(user_id)
        if not user:
            error = UserNotFoundError(user_id)
            logger.info(error)
            raise error
        return user

    async def get_user_by_email(self, *, email: str) -> User:
        """
        Fetches a user by their email address.

        :param email: User's email address to be retrieved
        :return: User object corresponding to the given email
        :raises UserNotFoundError: If no user is found with the specified email
        """
        stmt = select(User).where(User.email == email)
        user = await self.repository.find_one(stmt)
        if not user:
            error = UserNotFoundError(email)
            logger.info(error)
            raise error
        return user

    async def get_users_count(self) -> int:
        """
        Counts the number of users in the repository.

        :return: Number of users in the repository as an integer.
        """
        return await self.repository.count()

    async def get_active_users_count(self) -> int:
        """
        Fetches the active users count from the database.

        :return: Count of active users as an integer
        :rtype: int
        """
        query = (
            select(func.count())
            .select_from(User)
            .filter(User.status == StatusEnum.ACTIVE)
        )
        return await self.repository.count(query)

    async def get_admin_users_count(self) -> int:
        """
        Fetches the number of users with an 'ADMIN' role asynchronously.

        :return: Number of admin users
        :rtype: int
        """
        query = (
            select(func.count()).select_from(User).filter(User.role == RoleEnum.ADMIN)
        )
        return await self.repository.count(query)

    async def create_user(self, *, create_dict: dict[str, Any]) -> User:
        """
        Creates a new user with the provided details.

        :param create_dict: Dictionary containing user details. Must include "password".
        :return: The newly created User object.
        :raises UserCreateError: If there is an integrity error during user creation.

        Example usage:

            create_dict = {
                "email": "user@example.com",
                "password": "securepassword123"
            }
            new_user = await create_user(create_dict=create_dict)
        """
        create_dict.update(
            {
                "hashed_password": get_password_hash(create_dict["password"]),
                "status": StatusEnum.ACTIVE,
            }
        )
        try:
            user = await self.repository.create(create_dict)
        except IntegrityError as e:
            logger.info(f"error creating user: {e}")
            raise UserCreateError(create_dict["email"]) from e

        if settings.EMAIL_ENABLED and user.email:  # pragma: no cover
            email_data = generate_new_account_email(
                email_to=user.email,
                username=user.email,
                password=create_dict["password"],
            )
            send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

        return user

    async def update_user(
        self, *, user_id: UUID, update_dict: dict[str, Any]
    ) -> User | None:
        """
        Updates a user based on the given user_id and update_dict dictionary

        :param user_id: Unique identifier for the user
        :param update_dict: Dictionary containing user fields to be updated
        :return: Updated User object or None if update fails
        :raises UserValueError: If there is an IntegrityError during update

        Example usage:
            await update_user(user_id=user_id, update_dict={"email": "new_email@example.com", "password": "new_password"})
        """
        password = update_dict.get("password")
        if password:
            update_dict.update({"hashed_password": get_password_hash(password)})
        try:
            return await self.repository.update(user_id, update_dict)
        except IntegrityError as e:
            logger.info(f"error updating user: {e}")
            raise UserValueError(update_dict["email"]) from e

    async def delete_user(self, *, user_id: UUID) -> None:
        """
        Deletes a user from the repository using the given user_id.
        If the user does not exist, raises UserNotFoundError.

        :param user_id: Unique identifier of the user to be deleted
        :return: None
        :raises UserNotFoundError: if user with user_id does not exist
        """
        deleted = await self.repository.delete(user_id)
        if not deleted:
            error = UserNotFoundError(user_id)
            logger.info(f"error deleting user: {error}")
            raise error

    async def authenticate(self, *, email: str, password: str) -> User | None:
        """
        Authenticate a user by their email and password.

        :param email: The email address of the user to authenticate
        :param password: The plaintext password for the user
        :return: The authenticated User object if credentials are valid, otherwise None

        Example:

        async def login():
            user = await user_service.authenticate(email="user@example.com", password="securepassword")
            if user:
                print("Successfully authenticated")
            else:
                print("Authentication failed")

        Error cases:
        - If the email does not correspond to any user, it returns None
        - If the password does not match the hashed password of the user, it returns None
        """
        try:
            user = await self.get_user_by_email(email=email)
        except UserNotFoundError:
            return None
        if not verify_password(password, user.hashed_password):
            logger.info(f"error verifying password for user: {user.id}")
            return None
        return user

    async def recover_password(self, email: str) -> None:
        """
        Sends a password recovery email to the user associated with the provided email address.

        :param email: The email address of the user requesting password recovery.
        :return: None

        The function works asynchronously:
        1. Retrieves the user object for the given email.
        2. Generates a password reset token.
        3. Constructs the content needed for the password reset email.
        4. Sends the password reset email to the user's email address.

        Raises an exception if the user with the specified email does not exist or sending the email fails.
        """
        user = await self.get_user_by_email(email=email)

        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
