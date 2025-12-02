update formhistory set status_id = "Approved" where status_id= 'Approved Reluctantly';
delete from status where statusName = "Approved Reluctantly";