CREATE TABLE art_pipeline_efficiencies(
    ID BIGINT PRIMARY KEY AUTO_INCREMENT,
    ArtID BIGINT NOT NULL,
    Minimum INT,
    Maximum INT,
    Average INT,
    Date DATE,
    FOREIGN KEY (ArtID) REFERENCES agile_release_trains(ID),
    UNIQUE KEY unique_art_daily_record (ArtID,Date)
);

ALTER TABLE art_pipeline_efficiencies MODIFY COLUMN Date DATE NOT NULL DEFAULT (CURRENT_DATE);