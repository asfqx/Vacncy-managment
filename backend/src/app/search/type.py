from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchExpression:
    
    match: Any
    score: Any