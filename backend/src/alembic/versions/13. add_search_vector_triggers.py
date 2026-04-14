"""add search vector triggers

Revision ID: 2d6b7b4b1f2a
Revises: c1aasd7as2d41
Create Date: 2026-04-14 16:45:00.000000
"""

from collections.abc import Sequence

from alembic import op


revision: str = "2d6b7b4b1f2a"
down_revision: str | Sequence[str] | None = "c1aasd7as2d41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.execute(
        """
        CREATE OR REPLACE FUNCTION app_build_search_vector(
            source_title text,
            source_body text
        )
        RETURNS tsvector
        LANGUAGE sql
        STABLE
        AS $$
            SELECT
                setweight(to_tsvector('simple', unaccent(coalesce(source_title, ''))), 'A')
                || setweight(to_tsvector('simple', unaccent(coalesce(source_body, ''))), 'B')
                || setweight(
                    to_tsvector(
                        'russian',
                        unaccent(coalesce(source_title, '') || ' ' || coalesce(source_body, ''))
                    ),
                    'C'
                )
                || setweight(
                    to_tsvector(
                        'english',
                        unaccent(coalesce(source_title, '') || ' ' || coalesce(source_body, ''))
                    ),
                    'C'
                );
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION vacancys_search_vector_set()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.search_vector := app_build_search_vector(NEW.title, NEW.description);
            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION resumes_search_vector_set()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.search_vector := app_build_search_vector(NEW.title, NEW.about_me);
            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_vacancys_search_vector ON vacancys")
    op.execute(
        """
        CREATE TRIGGER trg_vacancys_search_vector
        BEFORE INSERT OR UPDATE OF title, description
        ON vacancys
        FOR EACH ROW
        EXECUTE FUNCTION vacancys_search_vector_set()
        """
    )

    op.execute("DROP TRIGGER IF EXISTS trg_resumes_search_vector ON resumes")
    op.execute(
        """
        CREATE TRIGGER trg_resumes_search_vector
        BEFORE INSERT OR UPDATE OF title, about_me
        ON resumes
        FOR EACH ROW
        EXECUTE FUNCTION resumes_search_vector_set()
        """
    )

    op.execute(
        """
        UPDATE vacancys
        SET search_vector = app_build_search_vector(title, description)
        """
    )
    op.execute(
        """
        UPDATE resumes
        SET search_vector = app_build_search_vector(title, about_me)
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_resumes_search_vector ON resumes")
    op.execute("DROP TRIGGER IF EXISTS trg_vacancys_search_vector ON vacancys")
    op.execute("DROP FUNCTION IF EXISTS resumes_search_vector_set()")
    op.execute("DROP FUNCTION IF EXISTS vacancys_search_vector_set()")
    op.execute("DROP FUNCTION IF EXISTS app_build_search_vector(text, text)")
