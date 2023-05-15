from typing import List

from fastapi import Depends, HTTPException, Request, status

from src.database.models import Role, User
from src.conf.messages import MSC403_FORBIDDEN
from src.services.auth import AuthUser


authuser = AuthUser()  # ! import from users?


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(authuser.get_current_user)):  # AuthUser
        # To log:
        # print(request.method, request.url)
        # print(f'User role {current_user.roles}')
        # print(f'Allowed roles: {self.allowed_roles}')
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MSC403_FORBIDDEN)


allowed_all_roles_access = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_delete = RoleAccess([Role.admin])
