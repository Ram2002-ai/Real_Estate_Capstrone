import sys
import pickle
import sklearn.compose._column_transformer as _column_transformer

# Monkey patch the missing class
class _RemainderColsList(list):
    pass

# Inject it into the module where pickle expects it
setattr(_column_transformer, '_RemainderColsList', _RemainderColsList)

try:
    print("Attempting to load pipeline.pkl...")
    with open('files/pkl.files/pipeline.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
    
    # Re-save with current sklearn version to fix future loads
    # When saving, it should use the current structure (hopefully not referencing _RemainderColsList anymore if we didn't use it?)
    # Actually, if the object IS a _RemainderColsList, it will try to save it as such.
    # We might need to convert it or just save it and hope the patch works for loading too.
    # But usually sklearn updates internal state on load if version mismatches are handled, or we just need to re-save to update protocol.
    
    with open('files/pkl.files/pipeline.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model re-saved successfully to pipeline.pkl")

except Exception as e:
    print(f"Failed to fix pickle: {e}")
