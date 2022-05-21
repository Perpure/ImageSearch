CREATE EXTENSION IF NOT EXISTS pg_trgm;
SET search_path TO public;

DROP INDEX IF EXISTS publication_idx;
DROP INDEX IF EXISTS image_idx;
DROP INDEX IF EXISTS comment_idx;

CREATE INDEX publication_idx ON publication USING GIN (to_tsvector('russian', text));
CREATE INDEX image_idx ON image USING GIN (to_tsvector('russian', text));
CREATE INDEX comment_idx ON comment USING GIN (to_tsvector('russian', text));

DROP TABLE IF EXISTS words;

CREATE TABLE words AS
SELECT DISTINCT word
FROM ts_stat($$
        SELECT to_tsvector('russian', text) FROM publication
        UNION SELECT to_tsvector('russian', text) FROM image
        UNION SELECT to_tsvector('russian', text) FROM comment
    $$);

ALTER TABLE words ADD UNIQUE (word);

CREATE OR REPLACE FUNCTION update_words() RETURNS TRIGGER AS
$$
    BEGIN
        DROP TABLE IF EXISTS temp_inserted;

        CREATE TEMP TABLE temp_inserted AS
        SELECT text FROM inserted;

        INSERT INTO words
        SELECT word
        FROM ts_stat('SELECT to_tsvector(''russian'', text) FROM temp_inserted')
        ON CONFLICT DO NOTHING;

        RETURN NULL;
    END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_publication_words ON publication;
DROP TRIGGER IF EXISTS update_comment_words ON comment;
DROP TRIGGER IF EXISTS update_image_words ON image;

CREATE TRIGGER update_publication_words
    AFTER INSERT
    ON publication
    REFERENCING NEW TABLE AS inserted
    FOR EACH STATEMENT
EXECUTE PROCEDURE update_words();

CREATE TRIGGER update_comment_words
    AFTER INSERT
    ON comment
    REFERENCING NEW TABLE AS inserted
    FOR EACH STATEMENT
EXECUTE PROCEDURE update_words();

CREATE TRIGGER update_image_words
    AFTER INSERT
    ON image
    REFERENCING NEW TABLE AS inserted
    FOR EACH STATEMENT
EXECUTE PROCEDURE update_words();

DROP INDEX IF EXISTS words_idx;
CREATE INDEX words_idx ON words USING GIN (word gin_trgm_ops);

CREATE OR REPLACE FUNCTION replace_query_with_existing_words(query varchar) RETURNS varchar
    AS $$ WITH query_words AS (
            SELECT (ts_lexize('russian_stem', regexp_split_to_table))[1] AS word
            FROM regexp_split_to_table(query, E'[^а-яА-Яеё]+')
            WHERE ts_lexize('russian_stem', regexp_split_to_table) IS NOT NULL
                  AND array_length(ts_lexize('russian_stem', regexp_split_to_table), 1) = 1
        ), query_fixed_word_candidates AS (
            SELECT DISTINCT ON (query_words.word)
                query_words.word AS word,
                words.word AS fixed_word,
                word_similarity(query_words.word, words.word) AS sml
            FROM words, query_words
            WHERE query_words.word <% words.word
              AND abs(length(query_words.word) - length(words.word)) < 2
            ORDER BY word, sml DESC
        ), query_fixed_words AS (
            SELECT CASE
                    WHEN query_fixed_word_candidates.fixed_word is NULL
                        THEN query_words.word
                    ELSE query_fixed_word_candidates.fixed_word
                END
                AS word
            FROM query_words LEFT OUTER JOIN query_fixed_word_candidates
            USING (word)
        ) SELECT string_agg(word, ' | ') FROM query_fixed_words
    $$ LANGUAGE SQL;

CREATE OR REPLACE VIEW all_text_data AS SELECT id, text FROM publication
UNION SELECT publication_id as id, text FROM image
UNION SELECT publication_id as id, text FROM comment;

CREATE OR REPLACE VIEW publication_with_rank AS SELECT *, NULL::real AS rank FROM publication;

CREATE OR REPLACE FUNCTION full_text_search(query varchar) RETURNS TABLE (LIKE publication_with_rank)
AS $$ WITH publication_ids AS (SELECT id,
             max(ts_rank(to_tsvector('russian', text),
                     to_tsquery(replace_query_with_existing_words(query)))) AS rank
      FROM all_text_data
      WHERE to_tsvector('russian', text) @@ to_tsquery(replace_query_with_existing_words(query))
      GROUP BY id)
        SELECT * FROM publication
        RIGHT OUTER JOIN
        publication_ids USING (id)
        ORDER BY rank DESC, date DESC
$$ LANGUAGE SQL;
