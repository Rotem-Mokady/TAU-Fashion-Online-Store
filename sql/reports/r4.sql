SELECT c.id,
	   c.name,
       c.price,
       c.inventory,
       CASE WHEN c.campaign = 1 THEN 'With Campain' ELSE 'With No Campain' END as campain_flag

FROM taufashion_10.cloths c