
/*
  Ingests processed revenue, feature, and sfdc data and transforms it into a UFR table.
*/

{{ config(materialized='table') }}

with sfdc_ufr as (

    select * from centerhq.public."sfdc_ufr"

),

revenue_feature_ufr as (

    select * from centerhq.public."client_user_telemetry_ufr"

)

select

revenue_feature_ufr.client_id,
revenue_feature_ufr.client_name,
revenue_feature_ufr.client_user_name,
revenue_feature_ufr.client_user_id,
revenue_feature_ufr.client_revenue,
revenue_feature_ufr.client_revenue_timestamp,
revenue_feature_ufr.client_feature_value_oop,
revenue_feature_ufr.client_feature_usage_timestamp_oop,
revenue_feature_ufr.client_feature_value_submission,
revenue_feature_ufr.client_feature_usage_timestamp_submission,
revenue_feature_ufr.client_feature_value_approval,
revenue_feature_ufr.client_feature_usage_timestamp_approval,
sfdc_ufr.client_sector,
sfdc_ufr.client_segment,
sfdc_ufr.client_ae,
sfdc_ufr.client_csm,
sfdc_ufr.client_static_timestamp,
sfdc_ufr.client_revenue_forecast,
sfdc_ufr.client_revenue_forecast_horizon,
sfdc_ufr.client_revenue_forecast_timestamp,
sfdc_ufr.client_revenue_forecast_customer_user,
sfdc_ufr.client_feature_growth_class_card_activation

from revenue_feature_ufr
left join sfdc_ufr on revenue_feature_ufr.client_id = sfdc_ufr.client_id
order by revenue_feature_ufr.client_id
