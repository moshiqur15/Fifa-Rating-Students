"""
Create/Update pickle file from student_scoring_model notebook
This saves the model functions for use in the webapp

Usage:
    python create_scoring_model_pkl.py
    
After editing student_scoring_model.ipynb:
1. Export changes to src/scoring_model.py
2. Run this script to update the pickle file
3. Restart the webapp to load the updated model
"""

import pickle
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from scoring_model import StudentScoringModel


def get_model_version_info(filepath):
    """Get version info from existing model file"""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        return {
            'version': getattr(model, 'model_version', 'unknown'),
            'created': getattr(model, 'created_date', 'unknown')
        }
    except Exception as e:
        print(f"⚠️  Could not read existing model: {e}")
        return None


def backup_existing_model(filepath):
    """Create backup of existing model"""
    if not os.path.exists(filepath):
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.replace('.pkl', f'_backup_{timestamp}.pkl')
    
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"📦 Backup created: {backup_path}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")


# Create/Update and save the model
if __name__ == "__main__":
    print("=" * 60)
    print("Student Scoring Model - Create/Update PKL")
    print("=" * 60)
    print()
    
    output_path = "models/student_scoring_model.pkl"
    
    # Check if model already exists
    existing_info = get_model_version_info(output_path)
    
    if existing_info:
        print(f"📋 Existing model found:")
        print(f"   Version: {existing_info['version']}")
        print(f"   Created: {existing_info['created']}")
        print()
        
        # Create backup before updating
        backup_existing_model(output_path)
        print()
    else:
        print("✨ No existing model found. Creating new model...")
        print()
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Create new model from latest code
    print("🔨 Building model from src/scoring_model.py...")
    model = StudentScoringModel()
    
    # Save to pickle file
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✅ Model saved to: {output_path}")
    print()
    
    # Verify it can be loaded
    print("🔍 Verifying model...")
    with open(output_path, 'rb') as f:
        loaded_model = pickle.load(f)
    
    print(f"✅ Model verified successfully!")
    print(f"   Version: {loaded_model.model_version}")
    print(f"   Created: {loaded_model.created_date}")
    print()
    
    # Show file size
    file_size = os.path.getsize(output_path)
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print()
    
    if existing_info:
        print("✨ Model updated successfully!")
    else:
        print("✨ Model created successfully!")
    
    print()
    print("💡 Next steps:")
    print("   1. Restart your webapp: python app.py")
    print("   2. The updated model will be automatically loaded")
    print("=" * 60)
