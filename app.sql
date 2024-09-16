CREATE TABLE sheet1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255),
    record_id INT,
    change_type ENUM('INSERT', 'UPDATE', 'DELETE')
);

ALTER TABLE sheet1 ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

DELIMITER //

CREATE TRIGGER after_insert_sheet1
AFTER INSERT ON sheet1
FOR EACH ROW
BEGIN
    INSERT INTO change_log (table_name, record_id, change_type, timestamp)
    VALUES ('sheet1', NEW.id, 'INSERT', NOW());
END;

CREATE TRIGGER after_update_sheet1
AFTER UPDATE ON sheet1
FOR EACH ROW
BEGIN
    INSERT INTO change_log (table_name, record_id, change_type, timestamp)
    VALUES ('sheet1', NEW.id, 'UPDATE', NOW());
END;

CREATE TRIGGER after_delete_sheet1
AFTER DELETE ON sheet1
FOR EACH ROW
BEGIN
    INSERT INTO change_log (table_name, record_id, change_type, timestamp)
    VALUES ('sheet1', OLD.id, 'DELETE', NOW());
END;

//

DELIMITER ;
