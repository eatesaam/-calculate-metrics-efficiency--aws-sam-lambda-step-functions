CREATE VIEW `VwArtPipelineEfficiencyConfigurations` 
    AS select 
        `art`.`ID` AS `ArtID`,
        `config`.`ID` AS `ConfigID`,
        `art`.`Name` AS `Name`,
        `config`.`Code` AS `Code`,
        `config`.`ExtraJQL` AS `ExtraJQL`,
        `start_field`.`Key` AS `StartFieldKey`,
        `start_field`.`Name` AS `StartFieldName`,
        `end_field`.`Key` AS `EndFieldKey`,
        `end_field`.`Name` AS `EndFieldName`,
        `art`.`JiraProgramLevelKey` AS `JiraProgramLevelKey`,
        `art`.`JiraTeamLevelKey` AS `JiraTeamLevelKey` 
    from (((`art_pipeline_efficiency_configurations` `config` join `agile_release_trains` `art` 
                on((`config`.`ArtID` = `art`.`ID`))) 
                    join `jira_custom_fields` `start_field` 
                        on((`config`.`StartJiraCustomFieldID` = `start_field`.`ID`))) 
                            join `jira_custom_fields` `end_field` 
                                on((`config`.`EndJiraCustomFieldID` = `end_field`.`ID`)))