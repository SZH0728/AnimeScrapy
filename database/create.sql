CREATE DATABASE IF NOT EXISTS anime;
USE anime;

-- Table: detail
CREATE TABLE IF NOT EXISTS detail (
    `id` INT NOT NULL AUTO_INCREMENT,

    `name` VARCHAR(128) NOT NULL,
    `translation` VARCHAR(128),
    `all` JSON,

    `year` YEAR,
    `season` ENUM('spring', 'summer', 'autumn', 'winter'),

    `time` DATE,
    `tag` JSON,
    `description` TEXT,

    `web` TINYINT,
    `webId` INT,

    `picture` VARCHAR(128),

    PRIMARY KEY (`id`),
    INDEX `index_year_season` (`year`, `season`)
);

-- Table: score
CREATE TABLE IF NOT EXISTS score (
    `id` INT NOT NULL AUTO_INCREMENT,
    `detailId` INT,

    `detailScore` JSON,
    `score` DECIMAL(4, 2),
    `vote` INT,

    `date` DATE,

    PRIMARY KEY (`id`, `date`),
    INDEX idx_score_detail_date (`detailId`, `date`),
    INDEX idx_score_date (`date`),
    INDEX idx_score_rank (`score` DESC, `vote` DESC)
)
PARTITION BY RANGE (YEAR(`date`) * 10 + QUARTER(`date`)) (
    PARTITION p2025q3 VALUES LESS THAN (20254),
    PARTITION p2025q4 VALUES LESS THAN (20261),
    PARTITION p2026q1 VALUES LESS THAN (20262),
    PARTITION p2026q2 VALUES LESS THAN (20263),
    PARTITION p2026q3 VALUES LESS THAN (20264),
    PARTITION p2026q4 VALUES LESS THAN (20271),
    PARTITION p2027q1 VALUES LESS THAN (20272),
    PARTITION p2027q2 VALUES LESS THAN (20273),
    PARTITION pFUTURE VALUES LESS THAN MAXVALUE
);

-- Table: name_map
CREATE TABLE name_map (
    `id` INT AUTO_INCREMENT PRIMARY KEY,

    `name` VARCHAR(256) NOT NULL,
    `detailId` INT NOT NULL,

    INDEX index_name (`name`)
);

-- Table: web
CREATE TABLE IF NOT EXISTS web (
    `id` INT NOT NULL AUTO_INCREMENT,

    `name` VARCHAR(16),
    `host` VARCHAR(16),

    `format` VARCHAR(16),

    `priority` TINYINT,

    PRIMARY KEY (`id`)
);

-- Table: cache
CREATE TABLE IF NOT EXISTS cache(
    `id` INT NOT NULL AUTO_INCREMENT,

    `name` VARCHAR(128),
    `translation` VARCHAR(128),
    `all` JSON,

    `year` YEAR,
    `season` ENUM('spring', 'summer', 'autumn', 'winter'),

    `time` DATE,
    `tag` JSON,
    `description` TEXT,

    `score` DECIMAL(4, 2),
    `vote` INT,
    `date` DATE NOT NULL,

    `web` TINYINT,
    `webId` INT,

    `picture` VARCHAR(128),

    PRIMARY KEY (`id`),
    INDEX idx_cache_web (`web`)
);

INSERT INTO web (`name`, `host`, `format`, `priority`) VALUE
('Bangumi', 'bangumi.tv', '/subject/{}', 10),
('Anikore', 'www.anikore.jp', '/anime/{}', 40),
('aniDB', 'anidb.net', '/anime/{}', 20),
('MyAnimeList', 'myanimelist.net', '/anime/{}', 30);
