#!/usr/bin/env python3
"""
Script to stitch all JSON review files into a final annotation CSV.
This script reads all JSON files from the output directory and creates a comprehensive CSV file.
"""

import json
import pandas as pd
import os
import glob
from datetime import datetime

def get_image_filename_from_path(image_path):
    """Convert image path to safe filename (same logic as in app.py)"""
    safe_filename = image_path.replace("/", "_").replace("\\", "_")
    if safe_filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        safe_filename = safe_filename.rsplit('.', 1)[0]
    return f"{safe_filename}.json"

def stitch_reviews_to_csv(output_dir="./output", output_csv="final_annotations.csv"):
    """
    Stitch all JSON review files into a final annotation CSV.
    
    Args:
        output_dir (str): Directory containing JSON review files
        output_csv (str): Output CSV filename
    
    Returns:
        str: Status message
    """
    try:
        # Get all JSON files from output directory
        json_pattern = os.path.join(output_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            return f"No JSON files found in {output_dir}"
        
        # List to store all review data
        all_reviews = []
        
        # Process each JSON file
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    review_data = json.load(f)
                
                # Extract data for CSV
                csv_row = {
                    'image_path': review_data.get('image_path', ''),
                    'original_crop1': review_data.get('crop1', ''),
                    'original_label1': review_data.get('label1', ''),
                    'original_crop2': review_data.get('crop2', ''),
                    'original_label2': review_data.get('label2', ''),
                    'reviewer_crop': review_data.get('reviewer_crop', ''),
                    'reviewer_labels': review_data.get('reviewer_labels', ''),
                    'comments': review_data.get('comments', ''),
                    'reviewer_username': review_data.get('reviewer_username', ''),
                    'review_timestamp': review_data.get('review_timestamp', ''),
                    'selected_annotation': review_data.get('selected_annotation', ''),
                    'json_filename': os.path.basename(json_file)
                }
                
                all_reviews.append(csv_row)
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue
        
        if not all_reviews:
            return "No valid review data found"
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(all_reviews)
        
        # Sort by image path for consistency
        df = df.sort_values('image_path')
        
        # Save to CSV
        df.to_csv(output_csv, index=False)
        
        return f"Successfully created {output_csv} with {len(all_reviews)} reviews from {len(json_files)} JSON files"
        
    except Exception as e:
        return f"Error creating CSV: {str(e)}"

def get_review_summary(output_dir="./output"):
    """
    Get summary of reviews in the output directory.
    
    Args:
        output_dir (str): Directory containing JSON review files
    
    Returns:
        dict: Summary statistics
    """
    try:
        json_pattern = os.path.join(output_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        summary = {
            'total_reviews': len(json_files),
            'reviewed_images': [os.path.basename(f) for f in json_files],
            'reviewers': set(),
            'latest_review': None
        }
        
        latest_timestamp = None
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    review_data = json.load(f)
                
                # Collect reviewer names
                reviewer = review_data.get('reviewer_username', '')
                if reviewer:
                    summary['reviewers'].add(reviewer)
                
                # Find latest review
                timestamp = review_data.get('review_timestamp', '')
                if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    summary['latest_review'] = {
                        'image': review_data.get('image_path', ''),
                        'reviewer': reviewer,
                        'timestamp': timestamp
                    }
                    
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                continue
        
        summary['reviewers'] = list(summary['reviewers'])
        return summary
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    # Run the stitching process
    print("Stitching JSON reviews to CSV...")
    result = stitch_reviews_to_csv()
    print(result)
    
    # Show summary
    print("\nReview Summary:")
    summary = get_review_summary()
    if 'error' not in summary:
        print(f"Total reviews: {summary['total_reviews']}")
        print(f"Reviewers: {', '.join(summary['reviewers'])}")
        if summary['latest_review']:
            print(f"Latest review: {summary['latest_review']['image']} by {summary['latest_review']['reviewer']}")
    else:
        print(f"Error getting summary: {summary['error']}")
