upload_and_parse_data = {
    "type": "function",
    "function": {
        "name": "upload_and_parse_data",
        "description": "Upload insurance documents to parse in PNG format",
        "parameters": {
            "type": "object",
            "properties": {
                "upload_image_file_for_extraction": {
                    "type": "string",
                    "description": "Ask user to upload insurane document in PNG format",
                },
            },
            "required": ["image_url"],
        },
    },
}

exit_from_upload_and_parse_data = {
    "type": "function",
    "function": {
        "name": "exit_from_upload_and_parse_data",
        "description": "If the user explicitly says that he wants to exit or not continue with the upload flow",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "State the exact kind of data that you want to pull based on above criteria",
                },
            },
            "required": ["query"],
        },
    },
}

answer_question_about_any_extracted_record = {
    "type": "function",
    "function": {
        "name": "get_details_about_any_extracted_record",
        "description": "If the user wants to Search/Find/Show/Query extracted health records based on query factors like emirates id, name of patient, fob, network, policy_start_date, policy_end_date, eligibility, payer name etc. Any one query factor is enough to trigger the function.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Detailed query (in verbose) with given field names and values",
                },
                "contains_keywords": {
                    "type": "array",
                    "description": "Array of values of keys from the query that should be present in document. (Main keys in our document is emirates_id, name, network, payer_name, fob)",
                    "items": {
                        "type": "string",
                        "description": "Values of keys from the query that should be present in document. (Main keys in our document is emirates_id, name, network, payer_name, fob",
                    },
                },
                "not_contains_keywords": {
                    "type": "array",
                    "description": "Array of values of keys from the query that should not be present in document. (Main keys in our document is emirates_id, name, network, payer_name, fob)",
                    "items": {
                        "type": "string",
                        "description": "Values of keys from the query that should not be be present in document. (Main keys in our document is emirates_id, name, network, payer_name, fob",
                    },
                },
            },
            "required": ["query", "contains_keywords", "not_contains_keywords"],
        },
    },
}

insurance_image_extraction_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "insurance_image_extraction_format",
        "schema": {
            "type": "object",
            "properties": {
                "if_uploaded_image_is_valid": {
                    "type": "boolean",
                    "description": "True if the image indeed contains insurance-related details of the patient and specific FOB. Else false.",
                },
                "response": {
                    "type": "object",
                    "properties": {
                        "emirates_id": {
                            "type": "string",
                            "description": "The Emirates ID of the individual. Should be a 15-digit unique identifier without any separators like '-' or ' '.",
                        },
                        "name": {
                            "type": "string",
                            "description": "The full name of the individual.",
                        },
                        "network": {
                            "type": "string",
                            "description": "Insurance network to which the person belongs.",
                        },
                        "policy_start_date": {
                            "type": "string",
                            "description": "The start date of the policy in YYYY-MM-DD format.",
                        },
                        "policy_end_date": {
                            "type": "string",
                            "description": "The end date of the policy in YYYY-MM-DD format.",
                        },
                        "payer_name": {
                            "type": "string",
                            "description": "The name of the payer or insurance provider.",
                        },
                        "fob": {
                            "type": "string",
                            "description": "FOB mentioned in the image.",
                        },
                        "eligibility": {
                            "type": "string",
                            "enum": ["eligible", "not_eligible", "pending"],
                            "description": "Indicates the individual's eligibility status.",
                        },
                        "gatekeeper_facility": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "Indicates if the availability of a gatekeeper facility is specifically mentioned in the image apart from the note section.",
                        },
                        "important_note": {
                            "type": "string",
                            "description": "Information available in the important note section or any other section in the main body of the image.",
                        },
                        "reason_for_ineligibility_if_any": {
                            "type": "string",
                            "description": "Indicates the reason for ineligibility, if mentioned. Else, it's empty.",
                        },
                        "specialist_consultation": {
                            "type": "string",
                            "description": "Mention the status of specialist consultation here.",
                        },
                        "coverage_details": {
                            "type": "string",
                            "description": "All coverage-related data in the coverage details section (if eligible) for this FOB is summarized here accurately. If not eligible, this is empty.",
                        },
                        "reply_to_user": {
                            "type": "string",
                            "description": "Message structure of this section: User is told that these are the extracted details. Then all key-value pairs extracted are displayed here (most important) in table format with proper punctuation (first letter of sentence capital, all enum values in verbose etc) for the user to see. Then the user is asked to confirm the key value pairs and also provide missing values if any are absent",
                        },
                    },
                    "required": [
                        "emirates_id",
                        "name",
                        "network",
                        "policy_start_date",
                        "policy_end_date",
                        "payer_name",
                        "reply_to_user",
                        "fob",
                        "eligibility",
                        "gatekeeper_facility",
                        "specialist_consultation",
                        "important_note",
                        "reason_for_ineligibility_if_any",
                        "coverage_details",
                    ],
                    "additionalProperties": False,
                },
            },
            "required": ["response", "if_uploaded_image_is_valid"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}


insurance_image_extraction_tool = {
    "type": "function",
    "function": {
        "name": "get_key_insurance_data_from_the_chatgpt_response",
        "description": "Get key details from the data extracted from insurance image",
        "parameters": {
            "type": "object",
            "properties": {
                "emirates_id": {
                    "type": "string",
                    "description": "The Emirates ID of the individual. Should be a 15-digit unique identifier. It cannot be empty or contain placeholder text like redacted, invalid, xxx etc",
                },
                "name": {
                    "type": "string",
                    "description": "The full name of the individual.",
                },
                "network": {
                    "type": "string",
                    "description": "Insurance network to which the person belongs to",
                },
                "policy_start_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The start date of the policy in YYYY-MM-DD format.",
                },
                "policy_end_date": {
                    "type": "string",
                    "format": "date",
                    "description": "The end date of the policy in YYYY-MM-DD format.",
                },
                "payer_name": {
                    "type": "string",
                    "description": "The name of the payer or insurance provider.",
                },
                "fob": {
                    "type": "string",
                    "enum": [
                        "op",
                        "ip_or_daycase",
                        "dental",
                        "optical",
                        "maternity",
                        "psychiatry",
                    ],
                    "description": "FOB mentioned in the image.",
                },
                "eligibility": {
                    "type": "string",
                    "enum": ["eligible", "not_eligible", "pending"],
                    "description": "Indicates the individual's eligibility status.",
                },
                "gatekeeper_facility": {
                    "type": "string",
                    "enum": ["yes", "no"],
                    "description": "Indicates if the availability of a gatekeeper facility is specifically mentioned in the image apart from the note section.",
                },
                "important_note": {
                    "type": "string",
                    "description": "Information available in the important note section or any other section in the main body of the image.",
                },
                "reason_for_ineligibility_if_any": {
                    "type": "string",
                    "description": "Indicates the reason for ineligibility, if mentioned, else left empty. Note: Cannot have value if eligible for coverage.",
                },
                "specialist_consultation": {
                    "type": "string",
                    "description": "Mention the status of specialist consultation here.",
                },
                "coverage_details": {
                    "type": "string",
                    "description": "All coverage-related data in the coverage details section for this FOB is summarized here accurately. Note: If not eligible or eligibility changed to ineligible/pending, this is empty.",
                },
                "image_url": {
                    "type": "string",
                    "description": "Url of the image uploaded",
                },
            },
            "required": [
                "emirates_id",
                "name",
                "policy_start_date",
                "policy_end_date",
                "eligibility",
                "payer_name",
                "network",
                "fob",
                "coverage_details",
                "specialist_consultation",
                "reason_for_ineligibility_if_any",
                "important_note",
                "gatekeeper_facility",
                "image_url",
            ],
        },
    },
}


search_query_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "search_query_response_format",
        "schema": {
            "type": "object",
            "properties": {
                "query_response": {
                    "type": "string",
                    "description": "Answer to the query based on given details",
                },
                "details_to_find_image_url": {
                    "type": "array",
                    "description": "Array of objects where emirates_id and list of relevant fobs related to a person mentioned in query_response are given",
                    "items": {
                        "type": "object",
                        "properties": {
                            "emirates_id": {
                                "type": "string",
                                "description": "Emirates ID of the person who is mentioned in query response",
                            },
                            "fob_associated": {
                                "type": "array",
                                "description": "List of relevant FOBs in the answer of the person with emirate id among OP, IP/Daycase, Dental, Optical, Maternity, Psychiatry",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "op",
                                        "ip_or_daycase",
                                        "dental",
                                        "optical",
                                        "maternity",
                                        "psychiatry",
                                    ],
                                },
                            },
                        },
                        "required": ["emirates_id", "fob_associated"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": [
                "query_response",
                "details_to_find_image_url",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
}
