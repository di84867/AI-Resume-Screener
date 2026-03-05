
import sys
# print("Python version:", sys.version)

try:
    import streamlit
    # print("Streamlit imported")
except ImportError as e:
    print("Streamlit import failed:", e)

try:
    import pypdf
    # print("pypdf imported")
except ImportError as e:
    print("pypdf import failed:", e)

try:
    import spacy
    # print("spacy imported")
    try:
        nlp = spacy.load("en_core_web_sm")
        # print("spacy model loaded")
    except OSError:
        print("spacy model 'en_core_web_sm' not found")
    except Exception as e:
        print("spacy model load failed:", e)
except ImportError as e:
    print("spacy import failed:", e)

try:
    import sklearn
    # print("scikit-learn imported")
except ImportError as e:
    print("scikit-learn import failed:", e)

try:
    import pandas
    # print("pandas imported")
except ImportError as e:
    print("pandas import failed:", e)

try:
    import numpy
    # print("numpy imported")
except ImportError as e:
    print("numpy import failed:", e)

try:
    import plotly
    # print("plotly imported")
except ImportError as e:
    print("plotly import failed:", e)

print("Environment check complete.")
