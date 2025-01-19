SELECT DISTINCT
	   s.age_category,
	   s.product_details as favorite_product_details

FROM
	(
	SELECT q.*,
		   max(q.total_amount_of_product) OVER (PARTITION BY q.age_category) as max_total_amount_of_product

	FROM
		(
		SELECT CASE WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 30 THEN 'UNDER 30'
					WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 40 THEN 'UNDER 40'
					ELSE '40 AND MORE' END as age_category,
			  concat ("Product ID: ", c.id, ", Product Name: ", c.name) as product_details,
			  sum(tti.amount) as total_amount_of_product

		FROM taufashion_10.users u

		JOIN taufashion_10.transactions t
		ON u.email = t.user_mail

		JOIN taufashion_10.transaction_to_items tti
		ON tti.transaction_id = t.id

		JOIN taufashion_10.cloths c
		ON tti.cloth_id = c.id

		GROUP BY CASE WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 30 THEN 'UNDER 30'
					WHEN TIMESTAMPDIFF(year,  u.birth_date, current_time()) < 40 THEN 'UNDER 40'
					ELSE '40 AND MORE' END,
				 concat ("Product ID: ", c.id, ", Product Name: ", c.name)
		) q
	) s

WHERE s.total_amount_of_product = s.max_total_amount_of_product

