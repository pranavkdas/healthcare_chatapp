from .backend_controller import backend_controller
from collections import deque


class websocket_chat_controller:
    def __init__(self):
        self.cache = {}
        self.backend_controller = backend_controller()
        super().__init__()

    def establish_connection(self, client_id="12312"):
        self.cache[client_id] = deque()

    def handle_cache_overflow(self, client_id):
        if len(self.cache[client_id]) > 30:
            self.cache[client_id].popleft()

    def get_chat_response(self, client_id, role, message, file_upload_status):
        self.cache[client_id].append({"role": role, "content": message})
        self.backend_controller.create_kafka_message(
            client_id, {"role": role, "content": message}
        )
        self.handle_cache_overflow(client_id)

        (
            response_by_assistant,
            file_upload_completed_bool,
        ) = self.backend_controller.get_response_to_chat(
            client_id, self.cache[client_id], file_upload_status
        )

        self.cache[client_id].append(
            {"role": "assistant", "content": response_by_assistant}
        )

        self.backend_controller.create_kafka_message(
            client_id, {"role": "assistant", "content": response_by_assistant}
        )

        return {
            "message": response_by_assistant,
            "file_upload_completed_bool": file_upload_completed_bool,
        }

    def upload_file_and_extract_data(self, client_id, role, binary_encoded_image):
        response = self.backend_controller.upload_file_and_extract_data(
            client_id, binary_encoded_image
        )
        ## WRITE CODE TO STORE IMAGE URL IN ANOTHER TABLE
        if response["valid_image"]:
            self.cache[client_id].append(
                {"role": "assistant", "content": response["message"]}
            )
            self.backend_controller.create_kafka_message(
                client_id, {"role": "assistant", "content": response["message"]}
            )
        return {"valid_image": response["valid_image"], "message": response["message"]}
