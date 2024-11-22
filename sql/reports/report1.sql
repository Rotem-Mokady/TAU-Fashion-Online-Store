select c.*,
	   coalesce(sum(t.amount), 0)  as counter

from taufashion_10.cloths c

left join taufashion_10.transactions t
on c.id = t.cloth_id

group by
	   c.id,
	   c.name,
       c.sex,
       c.path,
       c.price,
       c.inventory,
       c.campaign

order by counter desc


