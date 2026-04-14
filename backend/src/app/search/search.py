import re
from typing import Any

from sqlalchemy import case, func, literal, or_

from .constants import GENERIC_SEARCH_TERMS
from .type import SearchExpression




class SearchQueryBuilder:
    
    _token_pattern = re.compile(r"[^0-9A-Za-zА-Яа-яЁё]+")

    @classmethod
    def _tokens(cls, raw_query: str) -> list[str]:
        
        normalized_query = cls._token_pattern.sub(" ", raw_query.casefold())
        tokens: list[str] = []
        seen: set[str] = set()

        for token in normalized_query.split():
            if token in seen:
                continue

            tokens.append(token)
            seen.add(token)

        return tokens

    @classmethod
    def _normalized_query(cls, raw_query: str, *, remove_generic_terms: bool) -> str:
        
        tokens = cls._tokens(raw_query)
        if remove_generic_terms:
            focused_tokens = [
                token for token in tokens if token not in GENERIC_SEARCH_TERMS
            ]
            
            if focused_tokens:
                tokens = focused_tokens

        return " ".join(tokens)

    @staticmethod
    def _normalized_words(column: Any) -> Any:
        
        return func.trim(
            func.regexp_replace(
                func.lower(func.unaccent(column)),
                r"[^a-zа-я0-9]+",
                " ",
                "gi",
            )
        )

    @staticmethod
    def _ts_queries(query: Any) -> list[Any]:
        
        unaccent_query = func.unaccent(query)

        return [
            func.websearch_to_tsquery("simple", unaccent_query),
            func.websearch_to_tsquery("russian", unaccent_query),
            func.websearch_to_tsquery("english", unaccent_query),
        ]

    @staticmethod
    def _rank(search_vector: Any, ts_queries: list[Any]) -> Any:
        
        return func.greatest(
            *[
                func.coalesce(func.ts_rank_cd(search_vector, ts_query), 0.0)
                for ts_query in ts_queries
            ]
        )

    @classmethod
    def build(cls, raw_query: str, title: Any, search_vector: Any) -> SearchExpression | None:
        
        normalized_query = cls._normalized_query(raw_query, remove_generic_terms=False)
        focused_query = cls._normalized_query(raw_query, remove_generic_terms=True)

        if not normalized_query and not focused_query:
            return None

        if not focused_query:
            focused_query = normalized_query

        raw_query_sql = literal(normalized_query)
        focused_query_sql = literal(focused_query)
        use_raw_trgm = focused_query == normalized_query

        raw_ts_queries = cls._ts_queries(raw_query_sql)
        focused_ts_queries = cls._ts_queries(focused_query_sql)

        normalized_raw_query = func.lower(func.unaccent(raw_query_sql))
        normalized_focused_query = func.lower(func.unaccent(focused_query_sql))
        title_text = func.lower(func.unaccent(title))
        title_words = cls._normalized_words(title)

        title_query = func.websearch_to_tsquery("simple", func.unaccent(focused_query_sql))
        title_word_match = case(
            (
                func.to_tsvector("simple", title_words).op("@@")(title_query),
                1.0,
            ),
            else_=0.0,
        )

        rank = cls._rank(search_vector, raw_ts_queries)
        focused_rank = cls._rank(search_vector, focused_ts_queries)
        title_similarity = func.similarity(title_text, normalized_raw_query)
        focused_title_similarity = func.similarity(title_text, normalized_focused_query)

        score = (
            rank * 0.35
            + focused_rank * 1.15
            + ((title_similarity * 0.1) if use_raw_trgm else literal(0.0))
            + (focused_title_similarity * 0.35)
            + (title_word_match * 2.5)
        ).label("score")

        match_conditions: list[Any] = [
            *[search_vector.op("@@")(ts_query) for ts_query in raw_ts_queries],
            *[search_vector.op("@@")(ts_query) for ts_query in focused_ts_queries],
            focused_title_similarity > 0.3,
            title_word_match == 1.0,
        ]

        if use_raw_trgm:
            match_conditions.append(title_similarity > 0.25)

        return SearchExpression(match=or_(*match_conditions), score=score)
