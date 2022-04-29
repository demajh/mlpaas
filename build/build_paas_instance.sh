CONFIGNAME=$1

export INSTANCE_CONFIG=$CONFIGNAME

# Export key-value pairs in config to environment variables, accessible by paas templates
#for s in $(echo $values | jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]" ); do
#    export $s
#done

# Build data services
# Build data pipeline
# Build ML services
# Build ML pipelines
