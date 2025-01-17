from .connections import client_connections
from tenacity import retry, wait_random_exponential, stop_after_attempt
from .helper.tools import (
    upload_and_parse_data,
    insurance_image_extraction_tool,
    insurance_image_extraction_format,
    answer_question_about_any_extracted_record,
    exit_from_upload_and_parse_data,
    search_query_response_format
)
from .helper.system_messages import (
    system_instructions_for_confirmation_on_data_extracted,
    system_instructions_for_upload_and_search_tools,
    system_instructions_for_extracting_data_from_image,
    super_parent_system_query
)
import json
import os
import requests
import vercel_blob
import uuid
import base64

class backend_controller(client_connections):
    def __init__(self):
        super().__init__()
        # self.GPT_MODEL = "gpt-4o-mini"
        self.GPT_MODEL = "gpt-4o"

    @retry(
        wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3)
    )
    def openai_chat_completion_request(
        self, messages, tools=None, tool_choice=None, model=None, response_format=[]
    ):
        # remove later
        self.get_chromadb_client().heartbeat()
        #################

        try:
            openai_client = self.get_openai_client()
            response = openai_client.chat.completions.create(
                model=model if model else self.GPT_MODEL,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format if response_format else None,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def create_summary(self, data):
        sample_data = """The data pertains to an individual named Manju Tom who holds the Emirates ID number 78419932027238. This individual is associated with network RN4 and has a policy that starts on October 25, 2024, and ends on October 24, 2025. The payer for this insurance policy is Qatar Insurance Company.
        The fob category for this policy is identified as OP, denoting outpatient services. There are no reasons listed for any potential ineligibility. In terms of coverage details for outpatient services, a copayment of 20% is applicable for consultations, while there are no copayments expected for pharmaceutical services or other medical services. Physiotherapy is included under the coverage terms, ensuring that services are provided without any copayment requirements. The designated gatekeeper facility for this coverage is confirmed to be available, allowing access to healthcare services. However, there is an important note indicating that individuals must utilize hard gatekeeping facilities, specifically the Novitas Clinic, for all outpatient services. As a result, members are restricted to visiting only the gatekeeper clinic for these services. Specialist consultations are provided but require a referral in order to access them.
        """

        history_new = super_parent_system_query
        data_json_stringified = json.dumps(data)
        history_new.append({"role": "system", "content": f"Summarise the following json data in verbose without missing any data (especially fob) for later use in vector based search. Sample summary: {sample_data}"})
        history_new.append({"role": "system", "content": "The output should contain a plain text for all keys except coverage_details_for_specific_fobs in one paragraph and details related to different fobs in different paragraphs"})
        history_new.append({"role": "user", "content": data_json_stringified})

        new_summary_response = self.openai_chat_completion_request(
            messages=history_new
        )
        new_summary = new_summary_response.choices[0].message.content
        new_summary = new_summary.lower()

        return new_summary

    def create_kafka_message(self, client_id, message):
        # Write function to add them into messages column
        return

    def get_filtered_responses_from_search(self, query_given_by_user, contains_keywords, not_contains_keywords):
        chromadb = self.get_chromadb_client()
        chroma_collection = chromadb.get_or_create_collection(name="record_summaries")

        contains_query = [{"$contains": key.lower()} for key in contains_keywords]
        not_contains_query =  [{"$not_contains": key.lower()} for key in not_contains_keywords]
        where_document_query = contains_query + not_contains_query
        print('2222222222222222222222222')
        print(contains_keywords, not_contains_keywords)
        filtered_responses = {}
        if where_document_query:
            where_document_final_query = {"$and": where_document_query}
            if len(where_document_query)==1:
                where_document_final_query=where_document_query[0]
            filtered_responses = chroma_collection.query(
                query_texts=[query_given_by_user], # Chroma will embed this for you
                n_results=5, # how many results to return
                where_document = where_document_final_query
            )

        if filtered_responses.get("documents", []) and filtered_responses["documents"][0]:
            summary_messages = []
            for f in filtered_responses["documents"][0]:
                summary_messages.append({
                    "role": "system",
                    "content": f"These are summaries of the patient insurance datas: {f}"
                })

            user_query = [{
                "role": "user",
                "content": f"Answer the following query (to a good extend) using the filtered data given above: The query is: {query_given_by_user}",
            }]
            system_instructions = [{
                "role": "system",
                "content": "As Exec who is a responsible agent, ensure that you dont make up answers based on imagination to the query. Always answer based on information that is given to you. Otherwise you get a strike"
            }, {
                "role": "system",
                "content": "STRICTLY FOLLOW THE FOLLOWING RULES OR GET STRIKES \\\
                1. Exec must ensure that while forming the answer, each summary is considered and no relevant data is ignored\\\
                2. Only if Exec absolutely feels that multiple people might fit the answer to the user's query, he or should include them in the answers\\\
                3. All fobs and emirates id relevant to the answer to the user's query should be mentioned in the 'details_to_find_image_url' key of the response in the structure given there. \\\
                4. If any fob or emirate id that is relevant to the answer (to the user's query based on filtered info) is ignored, it will lead to 2 strikes instead of one\\\
                5. If any fob or emirate id that is irrelevant to the answer (to the user's query based on filtered info) is included, then it will lead to 2 strikes instead of one",
            }, {
                "role": "system",
                "content": "ALWAYS REPLY TO USER IN VERBOSE. IF SHOWING DATA, SHOW THEM USING BULLET POINTS",
                "type": "string",
            },
            ]
            new_query = super_parent_system_query + summary_messages + system_instructions + user_query

            response = self.openai_chat_completion_request(
                messages=new_query,
                response_format=search_query_response_format,

            )

            final_response = json.loads(response.choices[0].message.content)

            details_to_find_image_url = final_response["details_to_find_image_url"]
            metadatas = filtered_responses.get("metadatas")[0]
            print(details_to_find_image_url, 'details_to_find_image_url')
            print(len(filtered_responses["documents"][0]), query_given_by_user)

            final_string_to_add = ""
            if details_to_find_image_url:
                final_string_to_add = "\n Relevant image urls:- \n "
                for obj in details_to_find_image_url:
                    for metadata in metadatas:
                        if obj["emirates_id"] == metadata["emirates_id"]:
                            for key in obj["fob_associated"]:
                                if key in metadata:
                                    final_string_to_add += metadata[key] + " \n "

            return final_response["query_response"] + final_string_to_add + f"{details_to_find_image_url} details_to_find_image_url {query_given_by_user}"

        return "Sorry! Couldn't find any data that satisfies the query given. \n\n Note: It could also be that the query is too complex. Try using simpler queries"

    def get_response_to_chat(self, client_id, messages, file_upload_complete):
        tools_chain = []
        history = super_parent_system_query+list(messages.copy())
        if file_upload_complete:
            history += system_instructions_for_upload_and_search_tools
            tools_chain = [
                upload_and_parse_data,
                answer_question_about_any_extracted_record,
            ]
        else:
            history += system_instructions_for_confirmation_on_data_extracted
            tools_chain = [
                insurance_image_extraction_tool,
                exit_from_upload_and_parse_data,
            ]

        response = self.openai_chat_completion_request(
            messages=history,
            tools=tools_chain,
        )

        if getattr(response, "choices", ""):
            if getattr(response.choices[0].message, "tool_calls", ""):

                name_of_function = response.choices[0].message.tool_calls[0].function.name
                arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

                if name_of_function=="get_key_insurance_data_from_the_chatgpt_response":
                    mydb =self.get_mongodb_database()
                    chromadb = self.get_chromadb_client()
                    records_collection = mydb["insurance_records"]
                    query_response = list(records_collection.find({"emirates_id": arguments["emirates_id"]}))

                    if len(query_response) > 1: # This many not be required
                        return "Sorry, a person with this emirates_id already exists. Please try again", True

                    chroma_collection = chromadb.get_or_create_collection(name="record_summaries")

                    # our_object
                    keys_to_be_put_outside = ["emirates_id","name","network","policy_start_date","policy_end_date","payer_name"]
                    keys_to_be_put_inside = ["fob","eligibility","gatekeeper_facility","specialist_consultation","important_note","reason_for_ineligibility_if_any","coverage_details", "image_url"]
                    outside_object = {}
                    inside_object = {}
                    for key in keys_to_be_put_outside:
                        outside_object[key] = arguments[key]

                    for key in keys_to_be_put_inside:
                        inside_object[key] = arguments.get(key, "")

                    # Check if db already contains the file
                    entry = None
                    if query_response:
                        entry = query_response[0]
                        for out_key in keys_to_be_put_outside:
                            if out_key != "emirates_id":
                                entry[out_key] = outside_object[out_key]
                        inside_data = entry["coverage_details_for_specific_fobs"]
                        flag = False
                        for i in inside_data:
                            if i["fob"] == inside_object["fob"]:
                                flag = True
                                for key in keys_to_be_put_inside:
                                    if out_key != "emirates_id":
                                        i[key] = inside_object[key]
                        if not flag:
                            entry["coverage_details_for_specific_fobs"].append(inside_object)
                    else:
                        entry = {**outside_object, "coverage_details_for_specific_fobs": [inside_object]}

                    entry_for_summary = {}
                    for key in keys_to_be_put_outside:
                        entry_for_summary[key] = entry[key]

                    keys_to_be_put_outside.append("coverage_details_for_specific_fobs")

                    # for key in keys_to_be_put_inside
                    coverage_details = entry["coverage_details_for_specific_fobs"]
                    entry_for_summary["coverage_details_for_specific_fobs"] = []
                    image_url_metadata = {}
                    for fob_details in coverage_details:
                        temp_fob_object = {}
                        for key in fob_details:
                            if key!="image_url":
                                temp_fob_object[key] = fob_details[key]
                        entry_for_summary["coverage_details_for_specific_fobs"].append(temp_fob_object)

                        image_url_metadata[fob_details["fob"]]= fob_details["image_url"]

                    metadata_for_entry = {
                        "emirates_id": entry["emirates_id"],
                        **image_url_metadata
                    }

                    new_summary = self.create_summary(entry_for_summary)

                    records_collection.update_one({"emirates_id": entry["emirates_id"]} , {"$set": {k:entry[k] for k in keys_to_be_put_outside}}, upsert= True )

                    # Image url can be put in metadata
                    chroma_collection.upsert(
                        ids=[entry["emirates_id"]],
                        metadatas=metadata_for_entry,
                        documents=[new_summary],
                    )

                    return f"Successfully added the data for {entry["name"]} with Emirates ID {entry["emirates_id"]}", True

                elif name_of_function=="get_details_about_any_extracted_record":

                    query = arguments["query"].lower()
                    contains_keywords = arguments["contains_keywords"]
                    not_contains_keywords = arguments["not_contains_keywords"]
                    response = self.get_filtered_responses_from_search(query, contains_keywords, not_contains_keywords)
                    return response, file_upload_complete

                elif name_of_function == "exit_from_upload_and_parse_data":
                    # This should call function to delete the image url


                    return f"Cancelled uploading the extracted details successfully", True

            msg = response.choices[0].message.content
            return msg, file_upload_complete

        return "", file_upload_complete

    def upload_file_and_extract_data(self, client_id, base64_string):
        user_query = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract the text from the different fields in this image and use it to fill function. Use keys given in the function",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_string}"
                            },
                        },
                    ],
                }]
        history = super_parent_system_query+user_query + system_instructions_for_extracting_data_from_image
        response = self.openai_chat_completion_request(
            messages=history,
            response_format=insurance_image_extraction_format,
        )

        response_dict = json.loads(response.choices[0].message.content)
        
        bad_image_response = "Image not that of insurance data. Please upload another image"
        output = {"valid_image": response_dict["if_uploaded_image_is_valid"], "message": response_dict['response']["reply_to_user"] if response_dict["if_uploaded_image_is_valid"] else bad_image_response}
        
        if response_dict["if_uploaded_image_is_valid"]:

            # Decode the Base64 string
            # image_data = base64.b64decode(base64_string.split(",")[1])
            image_data_in_bytes = base64.b64decode(base64_string)

            request = vercel_blob.put(f'{str(uuid.uuid4())}.png', image_data_in_bytes)

            image_url = request.get("url", "")

            if not image_url: # If upload has error
                output["message"] = "Sorry. Please try again. Couldn't finish uploading the image"
                return output

            output["message"] += f"\n Uploaded image url: {image_url}"

        print(output)
        return output