# Convert the processed data into different schema

# Download data
# Group each doc into same dates
# Make document from each group
# Save each document as a date document

from datetime import datetime, timedelta
from database.api import get_all_processed_docs
from database.database import db


    