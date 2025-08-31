-- 创建anime_user用户并授权
CREATE USER IF NOT EXISTS 'anime_scrapy'@'%' IDENTIFIED BY 'anime_scrapy_password';

-- 授予anime数据库的所有权限
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER ON anime.* TO 'anime_scrapy'@'%';

-- 创建admin用户，允许外网访问并具有所有权限
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'docker_mariadb_admin_password';

-- 为admin用户授予所有权限
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 刷新权限
FLUSH PRIVILEGES;

