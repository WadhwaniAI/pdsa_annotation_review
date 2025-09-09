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
Reviewed annotations are saved to `assets/reviewed_annotations.csv` with:
- Original annotation index
- Image path
- Selected annotation set
- Reviewer's crop name and label
- Reviewer username and timestamp

## File Structure

```
pdsa-annotation-double/
├── app.py                                    # Main Gradio application
├── requirements.txt                          # Python dependencies
├── users.json                               # User authentication credentials
├── README.md                                # This file
└── assets/
    ├── double_annotations_for_review.csv    # Input annotations
    └── reviewed_annotations.csv             # Output reviews (created after first save)
```

## Configuration

### File Paths
Edit the following variables in `app.py` to customize:
- `CSV_FILE_PATH`: Path to input annotations CSV
- `OUTPUT_CSV_PATH`: Path for output reviews CSV
- `USERS_JSON_PATH`: Path to user credentials JSON file

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

## Security Note

This application uses simple authentication for demonstration. In production, implement proper password hashing and secure session management.
