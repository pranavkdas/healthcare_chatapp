# Standalone file. Not needed. Should be deleted later
import streamlit as st
from backend.connections import client_connections

if st.button("Clear data in both ChromaDB and MongoDB"):
	connection = client_connections()
	mongodb = connection.get_mongodb_database()
    chromadb = connection.get_chromadb_client()

    records_collection = mongodb["insurance_records"]

    records_collection.delete_many({})
	chromadb.delete_collection(name="record_summaries")