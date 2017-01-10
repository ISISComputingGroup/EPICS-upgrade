ALTER TABLE exp_data.experiment 
CHANGE COLUMN startDate startDate DATETIME NOT NULL ,
DROP PRIMARY KEY,
ADD PRIMARY KEY (experimentID, startDate);

ALTER TABLE exp_data.experimentteams 
DROP FOREIGN KEY experimentID;
ALTER TABLE exp_data.experimentteams 
ADD COLUMN experimentStart DATETIME NOT NULL AFTER roleID,
DROP PRIMARY KEY,
ADD PRIMARY KEY (experimentID, userID, roleID, experimentStart),
ADD INDEX experimentID_idx (experimentID ASC, experimentStart ASC);
ALTER TABLE exp_data.experimentteams 
ADD CONSTRAINT experimentID
  FOREIGN KEY (experimentID , experimentStart)
  REFERENCES exp_data.experiment (experimentID , startDate)
  ON DELETE CASCADE
  ON UPDATE CASCADE;
