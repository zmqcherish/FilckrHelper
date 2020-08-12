SELECT set_id, count(*) from img group by (set_id)

SELECT count(*) from img WHERE done=1
SELECT DISTINCT(title) from img WHERE set_id='72157637651260194'
SELECT * from img WHERE set_id='72157637651260194' and id in ('10977669084','10977735773','31274687016','32620964705','45395091752')
SELECT * from img WHERE id='45395091752'
SELECT * from img WHERE title like '%The Fivebar Swordtail - ผีเสื้อหางดาบใหญ่%'
SELECT DISTINCT(id) from img WHERE set_id='72157713017602853'

 -- update img set done=0 WHERE id = '17182720111'