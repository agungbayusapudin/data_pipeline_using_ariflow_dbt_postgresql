WITH product_rating_category AS (
    SELECT
        id,
        title,
        description,
        price,
        rating,
        CASE
            WHEN rating >= 4.5 THEN 'exelent'
            WHEN rating >= 4 THEN 'great'
            WHEN rating >= 3.5 THEN 'good'
            ELSE 'poor'
        END AS category_product
    FROM {{ ref('product')}}
),

review_category AS (
    SELECT
        rating,
        comment,
        date,
        id_product,
        id_review,
        CASE 
            WHEN rating >= 3.0 THEN 'positif'
            ELSE 'negatif'
        END AS rating_category
    FROM {{ ref('review_product')}}
)

SELECT
    p.id,
    p.title,
    p.description,
    p.price,
    p.category_product,
    r.rating,
    r.comment,
    r.date,
    r.rating_category
FROM product_rating_category p
JOIN review_category r ON p.id = r.id_product