from enum import StrEnum


class UserRole(StrEnum):
    
    ADMIN = "admin"
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    