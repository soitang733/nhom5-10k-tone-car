# Kết quả mở rộng mẫu 100 công ty

Danh sách gốc gồm đúng 100 ticker; mỗi công ty có 10 năm tài khóa FY2016–FY2025. SEC manifest có 1000 accession duy nhất, bảng tone và CAR cùng phiên có 1000 dòng của 100 công ty. Không bổ sung công ty ngoài CSV.

| Căn ngày | N | Hệ số | p HC3 | CI thấp | CI cao |
| --- | --- | --- | --- | --- | --- |
| same | 1000 | -0.40288 | 0.07130 | -0.84070 | 0.03494 |
| next | 1000 | -0.21843 | 0.30636 | -0.63697 | 0.20011 |
| acceptance | 1000 | -0.24790 | 0.25581 | -0.67548 | 0.17967 |


| outcome | specification | coefficient | se_HC3 | p_value | ci_low | ci_high | n | p_holm_all_reported_tests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_-1_1 | tone | -0.40288 | 0.22338 | 0.07130 | -0.84070 | 0.03494 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) | -0.43391 | 0.22513 | 0.05393 | -0.87515 | 0.00734 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) + C(ticker) | -0.59605 | 0.63379 | 0.34698 | -1.83825 | 0.64615 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.74541 | 0.27793 | 0.00732 | -1.29015 | -0.20068 | 794.00000 | 0.32199 |
| car_-3_3 | tone | -0.56458 | 0.28384 | 0.04669 | -1.12089 | -0.00827 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) | -0.57236 | 0.28326 | 0.04332 | -1.12754 | -0.01717 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) + C(ticker) | -0.31909 | 0.90942 | 0.72568 | -2.10152 | 1.46334 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.88857 | 0.33806 | 0.00858 | -1.55116 | -0.22599 | 794.00000 | 0.36884 |
| car_-5_5 | tone | -0.56145 | 0.35450 | 0.11324 | -1.25626 | 0.13335 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) | -0.59777 | 0.35373 | 0.09104 | -1.29106 | 0.09551 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) + C(ticker) | -1.02485 | 1.13283 | 0.36563 | -3.24515 | 1.19546 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.90634 | 0.40629 | 0.02570 | -1.70266 | -0.11002 | 794.00000 | 0.97651 |
| mar_-1_1 | tone | -0.32037 | 0.22715 | 0.15842 | -0.76557 | 0.12483 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) | -0.34000 | 0.22915 | 0.13787 | -0.78912 | 0.10912 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) + C(ticker) | -0.51905 | 0.64256 | 0.41921 | -1.77844 | 0.74034 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.64789 | 0.28513 | 0.02307 | -1.20673 | -0.08905 | 794.00000 | 0.92281 |


Nguồn kiểm toán: `data/companies_100_input.csv`, `data/filings_manifest.csv`, `data/extraction_audit.csv`, `outputs/real/*/car_panel.csv`.
