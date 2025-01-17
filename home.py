import streamlit as st
import uuid
from PIL import Image
from io import BytesIO
import base64
from backend.websocket_chat_controller import websocket_chat_controller


st.title("Search")
if "messages" not in st.session_state:
    print("Rerunning -------------------------------------------")
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! How may I help you?", "type": "string"},
    ]
    st.session_state["file_upload_complete"] = True

# Initialize session state variables
if "is_waiting" not in st.session_state:
    st.session_state.is_waiting = False  # Tracks if API call is in progress

if not st.session_state.get("websocket_server"):
    st.session_state["websocket_server"] = websocket_chat_controller()
    st.session_state["client_id"] = "1234"

    st.session_state["websocket_server"].establish_connection(
        st.session_state["client_id"]
    )


@st.dialog("Upload image to extract data")
def handle_upload_file():
    uploaded_file = st.file_uploader("Upload an image", type=["png"])

    # Check if an image is uploaded
    if uploaded_file is not None:
        # Open the uploaded image file

        file_bytes = uploaded_file.read()

        # Convert to Base64 string
        base64_string = base64.b64encode(file_bytes).decode("utf-8")

        image = Image.open(uploaded_file)

        # Display the image
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Upload and extract image"):
            with st.spinner("Uploading..."):
                file_upload_response = st.session_state[
                    "websocket_server"
                ].upload_file_and_extract_data(
                    st.session_state["client_id"], "user", base64_string
                )
                if not file_upload_response["valid_image"]:
                    st.error(file_upload_response["message"])
                else:
                    st.success("File uploaded successfully!")

                    handle_message_writes(base64_string, "user", "image")
                    st.session_state.messages.append(
                        {"role": "user", "content": base64_string, "type": "image"}
                    )

                    handle_message_writes(
                        file_upload_response["message"], "assistant", "string"
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": file_upload_response["message"],
                            "type": "string",
                        }
                    )
                    st.session_state["file_upload_complete"] = False

                    st.rerun()  # dialog closed when this is done - so find its proper place
    else:
        st.write("Please upload an image to proceed.")


def handle_message_writes(msg, role, type_of_msg):
    if type_of_msg == "string":
        msg_list = msg.split("\n")
        msg_list = [m.strip() for m in msg_list if m != ""]

        o1_bool = False
        o2_bool = False

        with st.chat_message(role):
            for i in range(len(msg_list)):
                m = msg_list[i]
                col1, col2 = st.columns([5, 2])
                m_lower = m.lower()
                with col1:
                    st.write(m)
                if (
                    role == "assistant"
                    and "upload" in m_lower
                    and (not o1_bool)
                    and "cancelled" not in m_lower
                    and "uploaded image url" not in m_lower
                    and "insurance" in m_lower
                ):
                    with col2:
                        st.button(
                            "Upload insurance data",
                            key=str(uuid.uuid4()),
                            on_click=handle_upload_file,
                        )
                    o1_bool = True

    elif type_of_msg == "image":
        with st.chat_message(role):
            # Decode the Base64 string back to image
            base_64_image = base64.b64decode(msg)
            decoded_image = Image.open(BytesIO(base_64_image))

            # Display the reconstructed image
            st.image(decoded_image, caption="Reconstructed Image")
            st.write("Image submitted for extracting data")


for msg in st.session_state.messages:
    if msg["role"] != "system":
        handle_message_writes(msg["content"], msg["role"], msg["type"])


# Display chat input and process messages
if not st.session_state["is_waiting"]:
    if prompt := st.chat_input():
        st.session_state["is_waiting"] = True  # Set waiting state
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "type": "string"}
        )
        st.chat_message("user").write(prompt)

        get_assistant_response = st.session_state["websocket_server"].get_chat_response(
            st.session_state["client_id"],
            "user",
            prompt,
            st.session_state["file_upload_complete"],
        )
        msg = get_assistant_response["message"]
        if get_assistant_response["file_upload_completed_bool"]:
            st.session_state["file_upload_complete"] = True

        handle_message_writes(msg, "assistant", "string")

        st.session_state.messages.append(
            {"role": "assistant", "content": msg, "type": "string"}
        )
        st.session_state["is_waiting"] = False  # Set waiting state
        st.rerun()
else:
    st.info("Waiting for API response...")
