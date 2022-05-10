CREATE TABLE jira_custom_fields(
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    `Key` VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    UNIQUE KEY `key` (`Key`),
    UNIQUE KEY name (Name)
);

