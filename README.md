RetailMart Data Pipeline
A small end-to-end data engineering pipeline built as part of a Junior Data Engineer technical assignment. It cleans, transforms, and loads daily retail sales data so the business team can use it for reporting.
Problem Statement
RetailMart Pvt. Ltd. runs a chain of retail stores across India and collects daily sales data from all its stores. The raw data is messy — spread across multiple CSV files with missing values and duplicates. This project builds a pipeline to clean, merge, and load that data, and answers key business questions:
Which products are selling the most, and in which city
Total revenue generated per store per day
Which stores or products have missing/incorrect data
Data Sources
File
Description
data/sales_data.csv
Daily sales transactions (sale_id, store_id, product_id, quantity, sale_date, amount) — contains intentional missing values and duplicate rows
data/products.csv
Product details (product_id, product_name, category, price)
data/stores.csv
Store details (store_id, store_name, city, region)
Pipeline Overview
The pipeline (pipeline.py) runs in six stages, all wired together through run_pipeline():
Data Ingestion — Load all three CSVs into pandas DataFrames; print shape, preview, and a missing-value summary.
Data Cleaning — Remove duplicate rows, fill missing quantity with 0, drop rows with missing amount, and fix data types (sale_date → datetime, amount → float).
Data Transformation — Merge sales, products, and stores into one DataFrame; calculate total_revenue (quantity × price) using NumPy; aggregate total revenue by city.
Data Loading (SQL) — Load the cleaned, merged DataFrame into a SQLite database (retail.db) as the retail_sales table; query the top 3 best-selling products by quantity.
Reporting & Insights — Query total revenue per store per day; print a summary report (total transactions, total revenue, top city, top product).
Error Handling — Each stage is wrapped in try/except so a missing or malformed source file prints a clear error message instead of crashing the pipeline.
How to Run
pip install pandas numpy
python pipeline.py

Sample Output Highlights
Duplicates removed: 2 rows
Rows after cleaning: 16
Top selling city: Mumbai
Top selling product: Parle-G Biscuit 200g
Total revenue (sample data): ₹12,330.00
Full console output is available in pipeline_output.txt.
Tech Stack
Python 3
pandas
NumPy
SQLite3 (via Python's built-in sqlite3 module)
