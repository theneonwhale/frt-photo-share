from typing import List

from fastapi import Depends, HTTPException, Request, status

from src.database.models import Role
from src.conf.messages import MSC403_FORBIDDEN
from src.services.auth import AuthUser


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: dict = Depends(AuthUser.get_current_user)):
        if current_user.get('roles') not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=MSC403_FORBIDDEN)


allowed_all_roles_access = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_admin_moderator = RoleAccess([Role.admin, Role.moderator])
