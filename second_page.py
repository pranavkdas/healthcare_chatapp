import streamlit as st

# from .backend.websocket_chat_controller import websocket_chat_controller
# from .backend.backend_controller import backend_logic_controller

# # a = backend_logic_controller()
# # b = websocket_chat_controller()
# # st.write(a.test())
# # st.write(b.test())
# # from streamlit_chat import message
# # from PIL import Image
# # import pytesseract
# # import openai
# # import os
# # import json
# # from uuid import uuid4

# # # Set your OpenAI API key
# # openai.api_key = "your-openai-api-key"

# # # Directory to store uploaded images
# # UPLOAD_DIR = "uploaded_images"
# # os.makedirs(UPLOAD_DIR, exist_ok=True)

# # # Initialize session states for conversation and data
# # if "messages" not in st.session_state:
# #     st.session_state.messages = [
# #         {
# #             "role": "assistant",
# #             "content": "Hello! I can help you process documents, extract information, and answer questions about them. Please upload an image of your document to get started.",
# #         }
# #     ]
# # if "document_data" not in st.session_state:
# #     st.session_state.document_data = {}


# # # Function: Extract text from image
# # def extract_text_from_image(image_path):
# #     text = pytesseract.image_to_string(Image.open(image_path))
# #     return text


# # # Function: Process user input
# # def process_user_input(user_input):
# #     # Check for upload prompt
# #     if "upload" in user_input.lower():
# #         return "Please upload an image of the document, and I'll extract its contents for you."

# #     # Check if a document has been processed
# #     if not st.session_state.document_data:
# #         return "You haven't uploaded a document yet. Please upload an image to begin."

# #     # Answer questions about the document
# #     document_id = next(
# #         iter(st.session_state.document_data.keys())
# #     )  # Get the first document
# #     document = st.session_state.document_data[document_id]
# #     query = user_input

# #     # Search in extracted text
# #     for section in document.get("sections", []):
# #         if query.lower() in section["text"].lower():
# #             return {
# #                 "answer": section["text"],
# #                 "image_reference": document["image_path"],
# #                 "page": section.get("page_number", 1),
# #             }
# #     return (
# #         "I couldn't find that information in the document. Please ask something else."
# #     )


# # # Main Streamlit UI
# # st.title("Conversational Document Assistant")

# # # Display the conversation
# # for msg in st.session_state.messages:
# #     if msg["role"] == "assistant":
# #         message(msg["content"], is_user=False)
# #     else:
# #         message(msg["content"], is_user=True)

# # # Upload file if prompted
# # uploaded_file = st.file_uploader("Upload a document image", type=["jpg", "jpeg", "png"])
# # if uploaded_file:
# #     file_id = str(uuid4())
# #     file_path = os.path.join(UPLOAD_DIR, f"{file_id}.jpg")
# #     with open(file_path, "wb") as f:
# #         f.write(uploaded_file.getbuffer())

# #     # Extract text from the uploaded image
# #     extracted_text = extract_text_from_image(file_path)
# #     st.session_state.document_data[file_id] = {
# #         "document_id": file_id,
# #         "sections": [{"section_id": str(uuid4()), "text": extracted_text}],
# #         "image_path": file_path,
# #     }

# #     # Add a system message confirming upload and processing
# #     st.session_state.messages.append(
# #         {
# #             "role": "assistant",
# #             "content": f"Document uploaded and processed successfully! You can now ask questions about the document.",
# #         }
# #     )

# # # Input box for the user
# # user_input = st.text_input("Your message:", key=uuid4())
# # if user_input:
# #     # Save user message
# #     st.session_state.messages.append({"role": "user", "content": user_input})

# #     # Process the input
# #     response = process_user_input(user_input)
# #     if isinstance(response, dict):  # If the response includes an image reference
# #         st.session_state.messages.append(
# #             {
# #                 "role": "assistant",
# #                 "content": f"I found this information: {response['answer']} (Page {response['page']}).",
# #             }
# #         )
# #         st.image(response["image_reference"], caption=f"Page {response['page']}")
# #     else:
# #         st.session_state.messages.append({"role": "assistant", "content": response})

# # # Scroll to the latest message
# # # st.rerun()
