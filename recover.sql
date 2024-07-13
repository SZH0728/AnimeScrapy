truncate anime.detail;
truncate anime.nameid;
truncate anime.score;
truncate anime.web;

load data infile 'D:/project/AnimeScrapy/backup/detail.txt' into table anime.detail fields terminated by '\t';
load data infile 'D:/project/AnimeScrapy/backup/nameid.txt' into table anime.nameid fields terminated by '\t';
load data infile 'D:/project/AnimeScrapy/backup/score.txt' into table anime.score fields terminated by '\t';
load data infile 'D:/project/AnimeScrapy/backup/web.txt' into table anime.web fields terminated by '\t';
