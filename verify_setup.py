
import sys
import os

output_file = r"c:\Users\singh\Desktop\AI-Resume-Screener\verify_result.txt"

print("Starting verification script...")
try:
    with open(output_file, "w") as f:
        f.write(f"Python: {sys.version}\n")
        print("Created verify_result.txt")
        
        try:
            import streamlit
            f.write("Streamlit: OK\n")
        except Exception as e:
            f.write(f"Streamlit: FAILED ({e})\n")
            
        try:
            import pypdf
            f.write("pypdf: OK\n")
        except Exception as e:
            f.write(f"pypdf: FAILED ({e})\n")
            
        try:
            import spacy
            f.write("spacy: OK\n")
            try:
                if not spacy.util.is_package("en_core_web_sm"):
                    from spacy.cli import download
                    download("en_core_web_sm")
                nlp = spacy.load("en_core_web_sm")
                f.write("model: OK\n")
            except Exception as e:
                f.write(f"model: FAILED ({e})\n")
        except Exception as e:
            f.write(f"spacy: FAILED ({e})\n")

        try:
            import sklearn
            f.write("sklearn: OK\n")
        except Exception as e:
            f.write(f"sklearn: FAILED ({e})\n")

        try:
            import pandas
            f.write("pandas: OK\n")
        except Exception as e:
            f.write(f"pandas: FAILED ({e})\n")

        try:
            import numpy
            f.write("numpy: OK\n")
        except Exception as e:
            f.write(f"numpy: FAILED ({e})\n")

        try:
            import plotly
            f.write("plotly: OK\n")
        except Exception as e:
            f.write(f"plotly: FAILED ({e})\n")


except Exception as main_e:
    print("Main script failed:", main_e)

print("Finished verification script.")
