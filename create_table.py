#!/usr/bin/env python3
"""
Create DynamoDB table for Richmond AI Agent
"""

import boto3
import sys

def create_richmond_table():
    """Create the richmond-data table in DynamoDB"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    table_name = 'richmond-data'
    
    # Check if table already exists
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table {table_name} already exists!")
        return table
    except:
        pass
    
    # Create table
    print(f"Creating table {table_name}...")
    
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Wait for table to be created
    print("Waiting for table to be created...")
    table.wait_until_exists()
    
    print(f"✅ Table {table_name} created successfully!")
    print(f"Table status: {table.table_status}")
    print(f"Item count: {table.item_count}")
    
    return table

if __name__ == "__main__":
    create_richmond_table()