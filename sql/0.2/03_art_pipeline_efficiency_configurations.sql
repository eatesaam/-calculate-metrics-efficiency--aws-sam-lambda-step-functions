CREATE TABLE art_pipeline_efficiency_configurations(
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    ArtID BIGINT NOT NULL,
    Name VARCHAR(50) NOT NULL,
    Code VARCHAR(50) NOT NULL,
    StartJiraCustomFieldID BIGINT NOT NULL,
    EndJiraCustomFieldID BIGINT NOT NULL,
    FOREIGN KEY (StartJiraCustomFieldID) REFERENCES jira_custom_fields(ID),
    FOREIGN KEY (EndJiraCustomFieldID) REFERENCES jira_custom_fields(ID),
    UNIQUE KEY code (Code)
);

ALTER TABLE art_pipeline_efficiency_configurations ADD COLUMN ExtraJQL TEXT;