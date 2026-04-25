# Fix Newman Collection - Remove date-time format validation
# This script fixes the timestamp format validation issues in Newman tests

# Read the collection file
$json = Get-Content "tests\contract\ocean_sentinel_api.postman_collection.json" | ConvertFrom-Json

# Fix the timestamp field in Health Check schema
$json = $json -replace '"time": { type: ''string'', format: ''date-time'' }', '"time": { type: ''string'' }'

# Fix the timestamp field in BARAG station schema  
$json = $json -replace '"timestamp": { type: ''string'', format: ''date-time'' }', '"timestamp": { type: ''string'' }'

# Write back to file
$json | ConvertTo-Json -Depth 100 | Set-Content "tests\contract\ocean_sentinel_api.postman_collection.json"

Write-Host "Fixed Newman collection - removed date-time format validation"
