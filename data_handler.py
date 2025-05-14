import os
import pickle
import numpy as np

class DataHandler:
    def __init__(self):
        self.data_dir = 'data'
        self.names_file = os.path.join(self.data_dir, 'names.pkl')
        self.faces_file = os.path.join(self.data_dir, 'faces_data.pkl')
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def clear_data(self):
        """Safely remove existing data files"""
        try:
            if os.path.exists(self.names_file):
                os.remove(self.names_file)
            if os.path.exists(self.faces_file):
                os.remove(self.faces_file)
            return True
        except Exception as e:
            print(f"Error clearing data: {str(e)}")
            return False
    
    def save_data(self, name, face_data):
        """Save face data and name with validation"""
        try:
            # Validate inputs
            if not isinstance(name, str) or len(name.strip()) == 0:
                raise ValueError("Invalid name provided")
            if not isinstance(face_data, np.ndarray):
                raise ValueError("Invalid face data format")
                
            # Initialize or load existing data
            names = []
            faces = None
            
            if os.path.exists(self.names_file) and os.path.exists(self.faces_file):
                try:
                    with open(self.names_file, 'rb') as f:
                        names = pickle.load(f)
                    with open(self.faces_file, 'rb') as f:
                        faces = pickle.load(f)
                except:
                    print("Warning: Previous data files corrupted, starting fresh")
            
            # Add new data
            names.extend([name] * len(face_data))
            if faces is not None:
                faces = np.vstack((faces, face_data))
            else:
                faces = face_data
                
            # Save data safely
            with open(self.names_file + '.tmp', 'wb') as f:
                pickle.dump(names, f)
            with open(self.faces_file + '.tmp', 'wb') as f:
                pickle.dump(faces, f)
                
            # If saves were successful, rename temp files to final names
            os.replace(self.names_file + '.tmp', self.names_file)
            os.replace(self.faces_file + '.tmp', self.faces_file)
            
            print(f"Successfully saved data for {name}")
            return True
            
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            # Clean up temp files if they exist
            for temp_file in [self.names_file + '.tmp', self.faces_file + '.tmp']:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return False
    
    def load_data(self):
        """Load and validate face data"""
        try:
            if not os.path.exists(self.names_file) or not os.path.exists(self.faces_file):
                print("No face data found. Please add face data first.")
                return None, None
                
            with open(self.names_file, 'rb') as f:
                names = pickle.load(f)
            with open(self.faces_file, 'rb') as f:
                faces = pickle.load(f)
                
            # Validate loaded data
            if not isinstance(names, list) or len(names) == 0:
                raise ValueError("Invalid names data")
            if not isinstance(faces, np.ndarray):
                raise ValueError("Invalid faces data")
                
            return faces, names
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None, None