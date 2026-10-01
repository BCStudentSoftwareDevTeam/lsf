-- This is where new changes go while in development
ALTER TABLE emailtracker ALTER COLUMN `subject` SET DEFAULT '';

ALTER TABLE `emailtracker` ADD `template_id` int NOT NULL DEFAULT 0;
ALTER TABLE `emailtracker` ADD `recipientEmails` varchar(255) NOT NULL DEFAULT '';
ALTER TABLE `emailtracker` ADD `body` varchar(255) NOT NULL DEFAULT '';
