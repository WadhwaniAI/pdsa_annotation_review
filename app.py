import gradio as gr
import pandas as pd
import os
import json
from typing import List, Tuple, Optional
import hashlib
import secrets
from PIL import Image

# Configuration
CSV_FILE_PATH = "/home/ashishp_wadhwaniai_org/pdsa-annotation-double/assets/double_annotations_for_review.csv"
OUTPUT_DIR = "/home/ashishp_wadhwaniai_org/pdsa-annotation-double/output"
USERS_JSON_PATH = "/home/ashishp_wadhwaniai_org/pdsa-annotation-double/users.json"
LABELS_JSON_PATH = "/home/ashishp_wadhwaniai_org/pdsa-annotation-double/assets/labels.json"

# Load users from JSON file
def load_users() -> dict:
    """Load user credentials from JSON file"""
    try:
        with open(USERS_JSON_PATH, 'r') as f:
            data = json.load(f)
            return data.get("users", {})
    except FileNotFoundError:
        print(f"Error: {USERS_JSON_PATH} not found. Please create the users.json file.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing {USERS_JSON_PATH}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

# Load users at startup
USERS = load_users()

# Load labels from JSON file
def load_labels() -> dict:
    """Load crop labels from JSON file"""
    try:
        with open(LABELS_JSON_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {LABELS_JSON_PATH} not found.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing {LABELS_JSON_PATH}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading labels: {e}")
        return {}

LABELS = load_labels()

def get_crop_names() -> List[str]:
    """Get list of available crop names"""
    return list(LABELS.keys()) if LABELS else []

def get_issue_names(crop_name: str) -> List[str]:
    """Get list of issue names for a specific crop"""
    if not LABELS or crop_name not in LABELS:
        return []
    return list(LABELS[crop_name].values())

def get_issue_name_by_id(crop_name: str, issue_id: str) -> str:
    """Get issue name by crop and ID"""
    if not LABELS or crop_name not in LABELS:
        return ""
    return LABELS[crop_name].get(issue_id, "")

# Session management
active_sessions = {}

def authenticate(username: str, password: str) -> bool:
    """Simple authentication function"""
    if not USERS:
        return False
    return username in USERS and USERS[username] == password

def create_session(username: str) -> str:
    """Create a new session for authenticated user"""
    session_token = secrets.token_urlsafe(32)
    active_sessions[session_token] = {
        "username": username,
        "current_index": 0
    }
    return session_token

def verify_session(session_token: str) -> Optional[dict]:
    """Verify session token and return session data"""
    return active_sessions.get(session_token)

def load_annotations() -> pd.DataFrame:
    """Load annotations from CSV file"""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def parse_labels(label_str: str) -> List[str]:
    """Parse label string to list of labels"""
    try:
        # Handle different label formats
        if isinstance(label_str, str):
            # Remove brackets and quotes, split by comma
            cleaned = label_str.strip("[]'\"")
            if cleaned:
                labels = [label.strip().strip("'\"") for label in cleaned.split(",")]
                return [label for label in labels if label]
        return []
    except:
        return []

def format_labels_for_display(labels: List[str]) -> str:
    """Format labels for display"""
    if not labels:
        return "No labels"
    return ", ".join(labels)

def resize_image(image_path: str, max_size: int = 512) -> str:
    """Resize image to keep longest side at max_size pixels"""
    try:
        if not os.path.exists(image_path):
            return None
        
        with Image.open(image_path) as img:
            # Calculate new size maintaining aspect ratio
            width, height = img.size
            if width > height:
                new_width = max_size
                new_height = int((height * max_size) / width)
            else:
                new_height = max_size
                new_width = int((width * max_size) / height)
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to temp file
            temp_path = f"/tmp/resized_{os.path.basename(image_path)}"
            resized_img.save(temp_path)
            return temp_path
            
    except Exception as e:
        print(f"Error resizing image {image_path}: {e}")
        return image_path  # Return original path if resize fails

def get_current_annotation(df: pd.DataFrame, index: int) -> dict:
    """Get current annotation data"""
    if index >= len(df):
        return {}
    
    row = df.iloc[index]
    return {
        "image_path": row["image_path"],
        "crop1": row["crop1"],
        "label1": parse_labels(row["label1"]),
        "crop2": row["crop2"],
        "label2": parse_labels(row["label2"]),
        "index": index
    }

def save_reviewed_annotation(df: pd.DataFrame, index: int, selected_annotation: str, 
                           reviewer_crop: str, reviewer_label: str, comments: str, session_token: str) -> str:
    """Save reviewed annotation as JSON file for the specific image"""
    try:
        session = verify_session(session_token)
        if not session:
            return "Session expired. Please login again."
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Get the current annotation data
        row = df.iloc[index]
        image_path = row["image_path"]
        
        # Create filename from image path (replace / with _ and remove extension)
        safe_filename = image_path.replace("/", "_").replace("\\", "_")
        if safe_filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            safe_filename = safe_filename.rsplit('.', 1)[0]
        json_filename = f"{safe_filename}.json"
        json_path = os.path.join(OUTPUT_DIR, json_filename)
        
        # Prepare the annotation data
        annotation_data = {
            "image_path": image_path,
            "crop1": row["crop1"],
            "label1": row["label1"],
            "crop2": row["crop2"],
            "label2": row["label2"],
            "reviewer_crop": reviewer_crop,
            "reviewer_labels": reviewer_label,
            "comments": comments,
            "reviewer_username": session["username"],
            "review_timestamp": pd.Timestamp.now().isoformat(),
            "selected_annotation": selected_annotation
        }
        
        # Save as JSON file
        with open(json_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        
        return f"Review saved successfully by {session['username']} to {json_filename}"
        
    except Exception as e:
        return f"Error saving annotation: {str(e)}"

# Gradio Interface Functions
def login_interface(username: str, password: str):
    """Handle login"""
    if not USERS:
        return (
            gr.update(visible=True),   # Keep login visible
            gr.update(visible=False),  # Hide main interface
            "",
            "Error: No users configured. Please check users.json file."
        )
    
    if authenticate(username, password):
        session_token = create_session(username)
        return (
            gr.update(visible=False),  # Hide login
            gr.update(visible=True),   # Show main interface
            session_token,
            f"Welcome, {username}!"
        )
    else:
        return (
            gr.update(visible=True),   # Keep login visible
            gr.update(visible=False),  # Hide main interface
            "",
            "Invalid credentials. Please try again."
        )

def load_annotation_data(session_token: str, index: int):
    """Load and display annotation data"""
    session = verify_session(session_token)
    if not session:
        return "Session expired. Please login again.", None, None, None, None, None, None
    
    df = load_annotations()
    if df.empty:
        return "No annotations found.", None, None, None, None, None, None
    
    if index >= len(df):
        return f"Index {index} out of range. Total annotations: {len(df)}", None, None, None, None, None, None
    
    annotation = get_current_annotation(df, index)
    if not annotation:
        return "Error loading annotation.", None, None, None, None, None, None
    
    # Update session with current index
    session["current_index"] = index
    
    # Display image if it exists (resized)
    image_display = None
    if os.path.exists(annotation["image_path"]):
        image_display = resize_image(annotation["image_path"])
    
    return (
        f"Annotation {index + 1} of {len(df)}",
        image_display,
        annotation["crop1"],
        format_labels_for_display(annotation["label1"]),
        annotation["crop2"],
        format_labels_for_display(annotation["label2"]),
        gr.update(choices=["label1", "label2"], value="label1"),
        annotation["crop1"],  # current_crop_display
        format_labels_for_display(annotation["label1"]),  # current_label_display
        annotation["crop1"],  # reviewer_crop (hidden)
        format_labels_for_display(annotation["label1"]).split(", ") if format_labels_for_display(annotation["label1"]) else [],  # reviewer_label (hidden)
        ""  # comments (hidden)
    )

def on_annotation_selection_change(selected_annotation: str, session_token: str):
    """Handle annotation selection change"""
    session = verify_session(session_token)
    if not session:
        return "Session expired.", gr.update(), gr.update()
    
    df = load_annotations()
    if df.empty:
        return "No data loaded.", gr.update(), gr.update()
    
    index = session["current_index"]
    if index >= len(df):
        return "Invalid index.", gr.update(), gr.update()
    
    annotation = get_current_annotation(df, index)
    if not annotation:
        return "Error loading annotation.", gr.update(), gr.update()
    
    if selected_annotation == "label1":
        crop_name = annotation["crop1"]
        label_name = format_labels_for_display(annotation["label1"])
    else:
        crop_name = annotation["crop2"]
        label_name = format_labels_for_display(annotation["label2"])
    
    # Show current values in read-only displays
    return (
        "", 
        gr.update(value=crop_name),  # current_crop_display
        gr.update(value=label_name),  # current_label_display
        gr.update(value=crop_name),  # reviewer_crop (hidden)
        gr.update(value=label_name.split(", ") if label_name else []),  # reviewer_label (hidden)
        gr.update(value="")  # comments (hidden)
    )

def enter_edit_mode(current_crop: str, current_label: str):
    """Enter edit mode - show dropdowns and populate with current values"""
    crop_choices = get_crop_names()
    issue_choices = get_issue_names(current_crop) if current_crop in crop_choices else []
    
    # Parse current label (might be comma-separated)
    current_label_list = current_label.split(", ") if current_label else []
    
    return (
        gr.update(visible=False),  # Hide read-only displays
        gr.update(visible=False),
        gr.update(visible=True, choices=crop_choices, value=current_crop),  # Show crop dropdown
        gr.update(visible=True, choices=issue_choices, value=current_label_list),  # Show issue dropdown
        gr.update(visible=True)  # Show comments
    )

def exit_edit_mode():
    """Exit edit mode - hide dropdowns and show read-only displays"""
    return (
        gr.update(visible=True),   # Show read-only displays
        gr.update(visible=True),
        gr.update(visible=False),  # Hide dropdowns
        gr.update(visible=False),
        gr.update(visible=False)   # Hide comments
    )

def update_issue_dropdown(crop_name: str):
    """Update issue dropdown based on selected crop"""
    if not crop_name:
        return gr.update(choices=[], value=[])
    
    issue_choices = get_issue_names(crop_name)
    return gr.update(choices=issue_choices, value=[])

def save_annotation_review(selected_annotation: str, reviewer_crop: str, reviewer_label: list, comments: str, session_token: str):
    """Save the annotation review"""
    session = verify_session(session_token)
    if not session:
        return "Session expired. Please login again."
    
    df = load_annotations()
    if df.empty:
        return "No annotations loaded."
    
    index = session["current_index"]
    if index >= len(df):
        return "Invalid annotation index."
    
    # Handle multi-select labels
    if isinstance(reviewer_label, list):
        reviewer_label_str = ", ".join(reviewer_label) if reviewer_label else ""
    else:
        reviewer_label_str = str(reviewer_label) if reviewer_label else ""
    
    if not reviewer_crop.strip() or not reviewer_label_str.strip():
        return "Please provide both crop name and at least one issue."
    
    result = save_reviewed_annotation(df, index, selected_annotation, reviewer_crop, reviewer_label_str, comments, session_token)
    return result

def next_annotation(session_token: str):
    """Move to next annotation"""
    session = verify_session(session_token)
    if not session:
        return 0, "Session expired."
    
    df = load_annotations()
    if df.empty:
        return 0, "No annotations loaded."
    
    current_index = session["current_index"]
    next_index = min(current_index + 1, len(df) - 1)
    session["current_index"] = next_index
    
    return next_index, f"Moved to annotation {next_index + 1}"

def previous_annotation(session_token: str):
    """Move to previous annotation"""
    session = verify_session(session_token)
    if not session:
        return 0, "Session expired."
    
    df = load_annotations()
    if df.empty:
        return 0, "No annotations loaded."
    
    current_index = session["current_index"]
    prev_index = max(current_index - 1, 0)
    session["current_index"] = prev_index
    
    return prev_index, f"Moved to annotation {prev_index + 1}"

# Create Gradio Interface
def create_interface():
    with gr.Blocks(title="Annotation Review Tool", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🌾 PDSA Annotation Review Tool")
        gr.Markdown("Review and verify crop annotations with authentication")
        
        # Session token (hidden)
        session_token = gr.State("")
        
        # Login Interface
        with gr.Row(visible=True) as login_row:
            with gr.Column():
                gr.Markdown("## Login")
                username_input = gr.Textbox(label="Username", placeholder="Enter username")
                password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password")
                login_btn = gr.Button("Login", variant="primary")
                login_status = gr.Markdown("")
        
        # Main Interface
        with gr.Row(visible=False) as main_row:
            with gr.Column(scale=1):
                gr.Markdown("## Navigation")
                current_status = gr.Markdown("")
                
                with gr.Row():
                    prev_btn = gr.Button("← Previous", variant="secondary")
                    next_btn = gr.Button("Next →", variant="secondary")
                
                index_input = gr.Number(label="Go to Index", value=0, precision=0)
                load_btn = gr.Button("Load Annotation", variant="primary")
                
                gr.Markdown("## Review")
                annotation_selector = gr.Radio(
                    choices=["label1", "label2"], 
                    label="Select Annotation Set",
                    value="label1"
                )
                
                with gr.Row():
                    edit_btn = gr.Button("Edit Annotations", variant="secondary")
                    submit_btn = gr.Button("Submit Review", variant="primary")
                
                # Read-only display of current values
                current_crop_display = gr.Textbox(
                    label="Current Crop",
                    interactive=False,
                    visible=True
                )
                current_label_display = gr.Textbox(
                    label="Current Issues",
                    interactive=False,
                    visible=True
                )
                
                # Editable dropdowns (hidden by default)
                reviewer_crop = gr.Dropdown(
                    choices=[],
                    label="Reviewer Crop Name",
                    value="",
                    allow_custom_value=True,
                    visible=False
                )
                reviewer_label = gr.Dropdown(
                    choices=[],
                    label="Reviewer Issues",
                    value=[],
                    multiselect=True,
                    allow_custom_value=True,
                    visible=False
                )
                
                comments = gr.Textbox(
                    label="Comments (Optional)",
                    placeholder="Add any comments about this annotation...",
                    lines=3,
                    visible=False
                )
                
                save_status = gr.Markdown("")
            
            with gr.Column(scale=2):
                gr.Markdown("## Image and Annotations")
                image_display = gr.Image(label="Image", type="filepath")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Annotation Set 1")
                        crop1_display = gr.Textbox(label="Crop 1", interactive=False)
                        label1_display = gr.Textbox(label="Label 1", interactive=False)
                    
                    with gr.Column():
                        gr.Markdown("### Annotation Set 2")
                        crop2_display = gr.Textbox(label="Crop 2", interactive=False)
                        label2_display = gr.Textbox(label="Label 2", interactive=False)
        
        # Event Handlers
        login_btn.click(
            login_interface,
            inputs=[username_input, password_input],
            outputs=[login_row, main_row, session_token, login_status]
        )
        
        load_btn.click(
            load_annotation_data,
            inputs=[session_token, index_input],
            outputs=[current_status, image_display, crop1_display, label1_display, 
                    crop2_display, label2_display, annotation_selector, current_crop_display, 
                    current_label_display, reviewer_crop, reviewer_label, comments]
        )
        
        annotation_selector.change(
            on_annotation_selection_change,
            inputs=[annotation_selector, session_token],
            outputs=[save_status, current_crop_display, current_label_display, reviewer_crop, reviewer_label, comments]
        )
        
        reviewer_crop.change(
            update_issue_dropdown,
            inputs=[reviewer_crop],
            outputs=[reviewer_label]
        )
        
        edit_btn.click(
            enter_edit_mode,
            inputs=[current_crop_display, current_label_display],
            outputs=[current_crop_display, current_label_display, reviewer_crop, reviewer_label, comments]
        )
        
        submit_btn.click(
            save_annotation_review,
            inputs=[annotation_selector, reviewer_crop, reviewer_label, comments, session_token],
            outputs=[save_status]
        ).then(
            exit_edit_mode,
            inputs=[],
            outputs=[current_crop_display, current_label_display, reviewer_crop, reviewer_label, comments]
        )
        
        prev_btn.click(
            previous_annotation,
            inputs=[session_token],
            outputs=[index_input, current_status]
        ).then(
            load_annotation_data,
            inputs=[session_token, index_input],
            outputs=[current_status, image_display, crop1_display, label1_display, 
                    crop2_display, label2_display, annotation_selector, current_crop_display, 
                    current_label_display, reviewer_crop, reviewer_label, comments]
        )
        
        next_btn.click(
            next_annotation,
            inputs=[session_token],
            outputs=[index_input, current_status]
        ).then(
            load_annotation_data,
            inputs=[session_token, index_input],
            outputs=[current_status, image_display, crop1_display, label1_display, 
                    crop2_display, label2_display, annotation_selector, current_crop_display, 
                    current_label_display, reviewer_crop, reviewer_label, comments]
        )
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        allowed_paths=["/data/nagpur_data/imgs/maize", "/home/ashishp_wadhwaniai_org/pdsa-annotation-double"]
    )
