SELECT c.id,
	   c.name,
	   sum(tti.amount) as ordred_amount,
	   round((sum(tti.amount) / (SELECT sum(amount) FROM taufashion_10.transaction_to_items)) * 100, 3) as ordred_amount_percantage

FROM taufashion_10.cloths c

LEFT JOIN taufashion_10.transaction_to_items tti
ON c.id = tti.cloth_id

GROUP BY c.id,
		 c.name