#!/bin/bash

echo "Testing tire search API..."
curl -s "https://wheelstore.preview.emergentagent.com/api/products/tires/search?diameter=15&season=winter" | python3 -m json.tool | head -100
