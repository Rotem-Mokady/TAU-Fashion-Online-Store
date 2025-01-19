SELECT DISTINCT
	   s.faculty,
	   s.product_details as favorite_product_details

FROM
	(
	SELECT q.*,
		   max(q.total_amount_of_product) OVER (PARTITION BY q.faculty) as max_total_amount_of_product

	FROM
		(
		SELECT u.faculty,
			  concat ("Product ID: ", c.id, ", Product Name: ", c.name) as product_details,
			  sum(tti.amount) as total_amount_of_product

		FROM taufashion_10.users u

		JOIN taufashion_10.transactions t
		ON u.email = t.user_mail

		JOIN taufashion_10.transaction_to_items tti
		ON tti.transaction_id = t.id

		JOIN taufashion_10.cloths c
		ON tti.cloth_id = c.id

		GROUP BY u.faculty,
				 concat ("Product ID: ", c.id, ", Product Name: ", c.name)
		) q
	) s

WHERE s.total_amount_of_product = s.max_total_amount_of_product

