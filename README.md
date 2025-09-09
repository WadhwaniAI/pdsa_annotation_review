# PDSA Annotation Review Tool

A Gradio-based web application for reviewing and verifying crop annotations with authentication.

## Features

- **Authentication System**: Secure login with username/password
- **Annotation Review**: Compare two annotation sets (label1/crop1 vs label2/crop2)
- **Image Display**: View the original images alongside annotations
- **Interactive Selection**: Choose between annotation sets and modify labels
- **Navigation**: Browse through annotations with previous/next buttons
- **Save Reviews**: Export reviewed annotations to CSV

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:7860`

## Usage

### Login
- Username: `admin` / Password: `admin123`
- Username: `reviewer1` / Password: `reviewer123`
- Username: `reviewer2` / Password: `reviewer456`

### Review Process
1. **Navigate**: Use Previous/Next buttons or enter an index number
2. **View**: See the image and both annotation sets
3. **Select**: Choose between "label1" or "label2" annotation set
4. **Edit**: Modify the crop name and label in the text boxes
5. **Save**: Click "Save Review" to export your review

### Output
Reviewed annotations are saved as individual JSON files in the `output/` directory with:
- Original annotation index
- Image path
- Selected annotation set
- Reviewer's crop name and label
- Reviewer username and timestamp

To combine all reviews into a final CSV file, use the `combine_reviews.py` script.

## File Structure

```
pdsa-annotation-double/
├── app.py                                    # Main Gradio application
├── combine_reviews.py                        # Script to combine JSON reviews into CSV
├── requirements.txt                          # Python dependencies
├── users.json                               # User authentication credentials
├── README.md                                # This file
├── assets/
│   ├── double_annotations_for_review.csv    # Input annotations
│   └── labels.json                          # Crop label definitions
└── output/                                  # Directory for individual review JSON files
    ├── _data_nagpur_data_imgs_maize_*.json  # Individual review files
    └── ...
```

## Configuration

### File Paths
Edit the following variables in `app.py` to customize:
- `CSV_FILE_PATH`: Path to input annotations CSV
- `OUTPUT_DIR`: Directory for output review JSON files
- `USERS_JSON_PATH`: Path to user credentials JSON file
- `LABELS_JSON_PATH`: Path to crop labels JSON file

### User Authentication
User credentials are stored in `users.json`. To add or modify users:

1. Edit `users.json`:
```json
{
  "users": {
    "admin": "admin123",
    "reviewer1": "reviewer123",
    "reviewer2": "reviewer456",
    "newuser": "newpassword"
  }
}
```

2. Restart the application to load new credentials

**Security Note**: The application requires a valid `users.json` file to function. If the file is missing or corrupted, authentication will fail.

### Crop Labels Configuration
Crop labels are defined in `assets/labels.json`. This file contains label mappings for different crops:
- `rice`: 32 different rice disease/pest labels
- `cotton`: 25 different cotton disease/pest labels  
- `maize`: 31 different maize disease/pest labels
- `chilli`: 11 different chilli disease/pest labels
- `soyabean`: 23 different soyabean disease/pest labels
- `wheat`: 22 different wheat disease/pest labels
- `sorghum`: 23 different sorghum disease/pest labels
- `gram`: 17 different gram disease/pest labels
- `cumin`: 10 different cumin disease/pest labels
- `others`: 3 general categories

Each crop has numeric IDs mapped to descriptive label names. The application uses these mappings to provide consistent labeling across reviews.

## Combining Reviews

The `combine_reviews.py` script stitches all individual JSON review files into a comprehensive CSV file for final analysis.

### Usage

```bash
python combine_reviews.py
```

### Options

- `--output-dir`: Directory containing JSON review files (default: `./output`)
- `--output-csv`: Output CSV filename (default: `final_annotations.csv`)

### Example

```bash
python combine_reviews.py --output-dir ./output --output-csv my_final_annotations.csv
```

### Output

The script creates a CSV file with columns:
- `index`: Original annotation index
- `image_path`: Path to the image file
- `selected_annotation`: Which annotation set was selected (label1 or label2)
- `crop_name`: Final crop name from the review
- `label`: Final label from the review
- `reviewer`: Username of the reviewer
- `timestamp`: When the review was completed

## Workflow

1. **Setup**: Configure file paths and user credentials
2. **Review**: Use the web interface to review annotations
3. **Save**: Individual reviews are saved as JSON files in the output directory
4. **Combine**: Use `combine_reviews.py` to create a final CSV file
5. **Analyze**: Use the combined CSV for further analysis

## Security Note

This application uses simple authentication for demonstration. In production, we need to implement proper password hashing and secure session management.
