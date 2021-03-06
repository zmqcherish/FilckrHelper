SELECT set_id, count(*) from img group by (set_id)

SELECT count(*) from img WHERE done=0
SELECT DISTINCT(title) from img WHERE set_id='72157637651260194'
SELECT * from img WHERE set_id='72157626633824222' order by title
SELECT * from img WHERE id='30925340201' and set_id='72157638815462813'
SELECT * from img WHERE title like '%candied apple%' and set_id='72157626633781904'
SELECT DISTINCT(id) from img WHERE set_id='72157713017602853'

SELECT * from sets WHERE id='72157632291104868'
SELECT * from sets WHERE title like '%Insects%'
-- update img set done=0 WHERE id in ('6562509107','5977705062', '5977467614', '6313921519') and set_id='72157697789232781'