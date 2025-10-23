import pandas as pd
from db_config import get_db_connection

def export_pairs(csv_path="matches.csv"):
    conn = get_db_connection()
    # Get all waste items and all need items
    wastes = pd.read_sql("SELECT id as waste_id, category as giver_category, description as giver_description, location FROM waste_items", conn)
    needs = pd.read_sql("SELECT id as need_id, category as receiver_category, description as receiver_description, location as receiver_location FROM need_items", conn)

    # Create cartesian join (you can filter by location proximity before training to reduce size)
    wastes['key'] = 1
    needs['key'] = 1
    pairs = pd.merge(wastes, needs, on='key').drop('key', axis=1)

    # Join with logged labels if exist
    logs = pd.read_sql("SELECT * FROM match_logs", conn)
    pairs = pairs.merge(logs[['waste_id','need_id','matched']], how='left', left_on=['waste_id','need_id'], right_on=['waste_id','need_id'])
    pairs['matched'] = pairs['matched'].fillna(0).astype(int)  # Unlabeled -> 0 (or consider -1 for unknown)

    # Combine text fields
    pairs['combined'] = pairs['giver_category'].fillna('') + " " + pairs['giver_description'].fillna('') + " " + pairs['receiver_category'].fillna('') + " " + pairs['receiver_description'].fillna('')
    
    pairs.to_csv(csv_path, index=False)
    conn.close()
    print("Exported", len(pairs), "pairs to", csv_path)

if __name__ == "__main__":
    export_pairs()
