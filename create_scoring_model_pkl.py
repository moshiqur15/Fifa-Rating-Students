"""
Create pickle file from student_scoring_model notebook
This saves the model functions for use in the webapp
"""

import pickle
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))
from scoring_model import StudentScoringModel


# Create and save the model
if __name__ == "__main__":
    print("Creating Student Scoring Model pickle file...")
    
    model = StudentScoringModel()
    
    # Save to pickle file
    output_path = "models/student_scoring_model.pkl"
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✓ Model saved to: {output_path}")
    
    # Verify it can be loaded
    with open(output_path, 'rb') as f:
        loaded_model = pickle.load(f)
    
    print(f"✓ Model verified successfully!")
    print(f"  Version: {loaded_model.model_version}")
    print(f"  Created: {loaded_model.created_date}")
    print("\nModel is ready to use in the webapp!")
