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


class EducationLevel(StrEnum):
    
    SECONDARY = "SECONDARY"  
    SECONDARY_SPECIAL = "SECONDARY_SPECIAL" 
    INCOMPLETE_HIGHER = "INCOMPLETE_HIGHER"  
    BACHELOR = "BACHELOR"  
    SPECIALIST = "SPECIALIST"  
    MASTER = "MASTER"  
    POSTGRADUATE = "POSTGRADUATE"  
    DOCTORATE = "DOCTORATE"  


class Gender(StrEnum):
    
    MALE = "MALE"
    FEMALE = "FEMALE"
    