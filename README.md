# Horse Racing

## Outline

- This software is to predict horse racing.
- It is released under the MIT License, see LICENSE.txt

## Contents

- racefile_past.py
  - This script is to download race data in the past.
  - Please specify target races in `holdings_sampling.yml`
- horseinfo.py
  - This script is to download horse data in the past.
  - You can choose the range of their age.
- file2db_past.py
  - This script is to store data from file into database.
- statistics.py
  - This script is to generate statistical value.
  - Please specify target you need to generate.
- featuredb.py
  - This script is to make feature values for modeling.
- modeling.py
  - This script is to create a horse racing forecasting model.
