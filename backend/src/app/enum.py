from enum import StrEnum


class UserRole(StrEnum):
    
    ADMIN = "admin"
    CANDIDATE = "candidate"
    COMPANY = "company"


class UserStatus(StrEnum):

    ACTIVE = "ACTIVE"
    BANNED = "BANNED"

class VacancyStatus(StrEnum):

    ACTIVE = "ACTIVE"
    BANNED = "ARCHIVE"
