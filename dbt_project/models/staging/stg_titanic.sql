WITH source_data AS (
    SELECT * FROM {{ source('titanic_raw', 'raw_data') }}
),
renamed_and_casted AS (
    SELECT
        CAST("passengerid" AS INTEGER) AS passenger_id,
        CAST("survived" AS INTEGER) AS survived,
        CAST("pclass" AS INTEGER) AS pclass,
        CAST("name" AS VARCHAR) AS passenger_name,
        CAST("sex" AS VARCHAR) AS sex,
        COALESCE(CAST("age" AS FLOAT), 0.0) AS age,
        CAST("sibsp" AS INTEGER) AS siblings_spouces_count,
        CAST("parch" AS INTEGER) AS parents_children_count,
        CAST("ticket" AS VARCHAR) AS ticket,
        COALESCE(CAST("fare" AS FLOAT),0.0) AS fare,
        CAST("cabin" AS VARCHAR) AS cabin,
        CAST("embarked" AS VARCHAR) AS embarked
    FROM source_data
)

SELECT * FROM renamed_and_casted