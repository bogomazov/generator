
CREATE TABLE "category" (
    category_id serial PRIMARY KEY,
    category_title varchar(50),
    category_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE "article_tag" (
    article_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (article_id, tag_id)
);



CREATE TABLE "article" (
    article_id serial PRIMARY KEY,
    article_text text,
    article_title varchar(50),
    article_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    article_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE "tag" (
    tag_id serial PRIMARY KEY,
    tag_value varchar(50),
    tag_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tag_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE "article__tag"
    ADD CONSTRAINT fk_article__tag_article
    FOREIGN KEY (article_id)
    REFERENCES "article" (article_id);


ALTER TABLE "article__tag"
    ADD CONSTRAINT fk_article__tag_tag
    FOREIGN KEY (tag_id)
    REFERENCES "tag" (tag_id);

ALTER TABLE "article" ADD "category_id" INTEGER NOT NULL;
ALTER TABLE "article"
    ADD CONSTRAINT fk_article_category
    FOREIGN KEY (category_id)
    REFERENCES "category" (category_id);

CREATE OR REPLACE FUNCTION category_insertFunc() RETURNS trigger AS 'BEGIN
    NEW.category_updated = now();
    RETURN NEW;
    END;'
LANGUAGE 'plpgsql';

CREATE TRIGGER "category_updateTrigger" BEFORE UPDATE ON  "category"
FOR EACH ROW EXECUTE PROCEDURE category_insertFunc();



CREATE OR REPLACE FUNCTION article_insertFunc() RETURNS trigger AS 'BEGIN
    NEW.article_updated = now();
    RETURN NEW;
    END;'
LANGUAGE 'plpgsql';

CREATE TRIGGER "article_updateTrigger" BEFORE UPDATE ON  "article"
FOR EACH ROW EXECUTE PROCEDURE article_insertFunc();



CREATE OR REPLACE FUNCTION tag_insertFunc() RETURNS trigger AS 'BEGIN
    NEW.tag_updated = now();
    RETURN NEW;
    END;'
LANGUAGE 'plpgsql';

CREATE TRIGGER "tag_updateTrigger" BEFORE UPDATE ON  "tag"
FOR EACH ROW EXECUTE PROCEDURE tag_insertFunc();

