

import pandas as pd
import numpy as np
import sqlite3
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retail.db")


def load_data():
    """Load the three source CSV files into pandas DataFrames."""
    sales_path = os.path.join(DATA_DIR, "sales_data.csv")
    products_path = os.path.join(DATA_DIR, "products.csv")
    stores_path = os.path.join(DATA_DIR, "stores.csv")

    sales_df = pd.read_csv(sales_path)
    products_df = pd.read_csv(products_path)
    stores_df = pd.read_csv(stores_path)

    print("=" * 70)
    print("TASK 1: DATA INGESTION")
    print("=" * 70)

    for name, df in [("sales_data", sales_df), ("products", products_df), ("stores", stores_df)]:
        print(f"\n--- {name} ---")
        print(f"Shape: {df.shape}")
        print(df.head())

    print("\n--- Missing Value Summary ---")
    for name, df in [("sales_data", sales_df), ("products", products_df), ("stores", stores_df)]:
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if nulls.empty:
            print(f"{name}: no missing values")
        else:
            print(f"{name}:\n{nulls}")

    return sales_df, products_df, stores_df

def clean_data(sales_df):
    """Remove duplicates, handle missing values, fix data types."""
    print("\n" + "=" * 70)
    print("TASK 2: DATA CLEANING")
    print("=" * 70)

    # Step 3: remove duplicates
    before = sales_df.shape[0]
    sales_df = sales_df.drop_duplicates()
    after = sales_df.shape[0]
    print(f"\nDuplicates found and removed: {before - after}")

    # Step 4: fill missing quantity with 0, drop rows with missing amount
    sales_df["quantity"] = sales_df["quantity"].fillna(0)
    sales_df = sales_df.dropna(subset=["amount"])
    print(f"Cleaned DataFrame shape: {sales_df.shape}")

    # Step 5: fix data types
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
    sales_df["amount"] = sales_df["amount"].astype(float)
    sales_df["quantity"] = sales_df["quantity"].astype(int)

    print("\nData types after cleaning:")
    print(sales_df.dtypes)

    return sales_df


def transform_data(sales_df, products_df, stores_df):
    """Merge all dataframes and compute revenue metrics."""
    print("\n" + "=" * 70)
    print("TASK 3: DATA TRANSFORMATION")
    print("=" * 70)

    # Step 6: merge
    merged_df = sales_df.merge(products_df, on="product_id", how="left")
    merged_df = merged_df.merge(stores_df, on="store_id", how="left")
    print("\n--- Final Merged DataFrame ---")
    print(merged_df)

    # Step 7: total_revenue = quantity * price (using numpy)
    merged_df["total_revenue"] = np.multiply(merged_df["quantity"], merged_df["price"])
    print(f"\nMean total_revenue: {np.mean(merged_df['total_revenue']):.2f}")
    print(f"Max total_revenue:  {np.max(merged_df['total_revenue']):.2f}")
    print(f"Min total_revenue:  {np.min(merged_df['total_revenue']):.2f}")

    # Step 8: group by city
    city_revenue = (
        merged_df.groupby("city")["total_revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    print("\n--- Total Revenue per City (descending) ---")
    print(city_revenue)

    return merged_df


def load_to_sql(merged_df):
    """Load the final merged dataframe into a SQLite database."""
    print("\n" + "=" * 70)
    print("TASK 4: DATA LOADING (SQL)")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    df_to_save = merged_df.copy()
    df_to_save["sale_date"] = df_to_save["sale_date"].astype(str)  # sqlite-friendly
    df_to_save.to_sql("retail_sales", conn, if_exists="replace", index=False)
    print(f"\nLoaded {len(df_to_save)} rows into 'retail_sales' table in {DB_PATH}")

    # Step 10: Top 3 best-selling products by total quantity
    query_top_products = """
        SELECT product_name, SUM(quantity) AS total_quantity_sold
        FROM retail_sales
        GROUP BY product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 3;
    """
    top_products = pd.read_sql_query(query_top_products, conn)
    print("\n--- Top 3 Best-Selling Products (by quantity) ---")
    print(top_products)

    conn.close()
    return query_top_products, top_products


def generate_report(merged_df):
    """SQL query for revenue per store per day + Python summary report."""
    print("\n" + "=" * 70)
    print("TASK 5: REPORTING & INSIGHTS")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    # Step 11: total revenue per store per day
    query_store_day = """
        SELECT store_name, sale_date, SUM(total_revenue) AS daily_revenue
        FROM retail_sales
        GROUP BY store_name, sale_date
        ORDER BY sale_date, store_name;
    """
    store_day_revenue = pd.read_sql_query(query_store_day, conn)
    print("\n--- Total Revenue per Store per Day ---")
    print(store_day_revenue)
    conn.close()

    # Step 12: summary report
    total_transactions = len(merged_df)
    total_revenue = merged_df["total_revenue"].sum()
    top_city = merged_df.groupby("city")["total_revenue"].sum().idxmax()
    top_product = merged_df.groupby("product_name")["quantity"].sum().idxmax()

    print("\n--- SUMMARY REPORT ---")
    print(f"Total number of transactions : {total_transactions}")
    print(f"Total revenue                : {total_revenue:,.2f}")
    print(f"Top selling city             : {top_city}")
    print(f"Top selling product          : {top_product}")

    return query_store_day, store_day_revenue

def run_pipeline():
    """Run the full pipeline end-to-end with error handling."""
    try:
        sales_df, products_df, stores_df = load_data()
    except FileNotFoundError as e:
        print(f"ERROR: A required source file is missing -> {e}")
        return
    except Exception as e:
        print(f"ERROR while loading data: {e}")
        return

    try:
        sales_df = clean_data(sales_df)
    except Exception as e:
        print(f"ERROR while cleaning data: {e}")
        return

    try:
        merged_df = transform_data(sales_df, products_df, stores_df)
    except Exception as e:
        print(f"ERROR while transforming data: {e}")
        return

    try:
        load_to_sql(merged_df)
    except Exception as e:
        print(f"ERROR while loading data into SQL database: {e}")
        return

    try:
        generate_report(merged_df)
    except Exception as e:
        print(f"ERROR while generating report: {e}")
        return

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
