CREATE DATABASE IF NOT EXISTS anime;
USE anime;

-- Table: detail
CREATE TABLE IF NOT EXISTS detail (
    `id` INT NOT NULL AUTO_INCREMENT,

    `name` VARCHAR(64) NOT NULL,
    `translation` VARCHAR(64),
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

    PRIMARY KEY (`id`)
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

    `name` VARCHAR(64),
    `translation` VARCHAR(64),
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

    PRIMARY KEY (`id`)
);

INSERT INTO web (name, host, format, priority) VALUE
('Bangumi', 'bangumi.tv', '/subject/{}', 10),
('Anikore', 'www.anikore.jp', '/anime/{}', 40),
('aniDB', 'anidb.net', '/anime/{}', 20),
('MyAnimeList', 'myanimelist.net', '/anime/{}', 30);
