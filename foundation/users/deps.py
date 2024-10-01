from typing import Annotated, Tuple, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from foundation.core.deps import get_async_session
from foundation.core.repository import Repository
from foundation.users.models import User
from foundation.users.services import UserService
from fastapi import Request
from sqlalchemy import Select
from foundation.core.pagination import Paginator


def get_user_repository(
    async_session: AsyncSession = Depends(get_async_session),
) -> Repository[User]:  # pragma: no cover
    """
    Factory function to get a `Repository` instance for `User` entities.

    :param async_session: Database session used for querying
    :type async_session: AsyncSession
    :return: Repository instance for User entities
    :rtype: Repository[User]
    """
    return Repository(async_session, User)


UserRepositoryDep = Annotated[Repository[User], Depends(get_user_repository)]


def get_user_service(repository: UserRepositoryDep) -> UserService:  # pragma: no cover
    """
    Returns a UserService instance initialized with the given UserRepository dependency

    :param repository: An instance of UserRepositoryDep used to manage User entities.
    :return: A UserService instance that uses the provided repository.

    Example:
        repository = UserRepositoryDep()
        user_service = get_user_service(repository)
        # user_service can now be used for user-related operations

    Error Cases:
        None - Assumes valid UserRepositoryDep is provided.
    """
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


class UserPagination:
    """
    Manages pagination for User entities using a provided repository.

    :param repository: Repository for User entities.
    """

    repository: Repository[User]

    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def paginate(
        self,
        request: Request,
        query: Select[Tuple[Any]],
        order_by: str,
        asc: bool = True,
        page_size: int = 10,
    ):
        return Paginator(
            request,
            self.repository,
            query,
            page_size=page_size,
            order_by=order_by,
            ascending=asc,
        )


def get_user_pagination(
    repository: UserRepositoryDep,
) -> UserPagination:  # pragma: no cover
    """
    This function returns a UserPagination object, which handles pagination of user data using a provided repository.

    :param repository: The repository to fetch user data from
    :return: UserPagination object

    Example usage:

        repository = UserRepositoryDep()
        pagination = get_user_pagination(repository)
    """
    return UserPagination(repository)


UserPaginationDep = Annotated[UserPagination, Depends(get_user_pagination)]
