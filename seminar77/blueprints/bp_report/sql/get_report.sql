SELECT rep_id, p_amount, p_value, created_at
FROM product_report
WHERE p_month = %s AND p_year = %s
ORDER BY created_at DESC