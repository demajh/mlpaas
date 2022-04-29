
/*
    Transforms SFDC data to UFR representation.
*/

{{ config(materialized='table') }}

with source_data as (

    select

      "comdata account code" as client_id,
      "account name" as client_name,
      "industry" as client_sector,
      "employee segment" as client_segment,
      "account owner: full name" as client_ae,
      "account manager: full name" as client_csm,
      GETDATE() as client_static_timestamp,
      "sum of closed won annual spend" as client_revenue_forecast,
      'annual' as client_revenue_forecast_horizon,
      "application signed" as client_revenue_forecast_timestamp,
      "account owner: full name" as client_revenue_forecast_customer_user,
      "account_curve_class" as client_feature_growth_class_card_activation

    from centerhq.public."sfdc-data-labeled-max"

)

select *
from source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
