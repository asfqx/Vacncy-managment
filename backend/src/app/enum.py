from enum import StrEnum


class UserRole(StrEnum):
    
    ADMIN = "admin"
    CANDIDATE = "candidate"
    EMPLOYER = "employer"


class UserStatus(StrEnum):

    ACTIVE = "ACTIVE"
    BANNED = "BANNED"
