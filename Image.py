import google.generativeai as genai

from pathlib import Path


class Image:
    def __init__(self, gemini_token: str):
        self.media = Path('.')
        self.safety_config = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }
        self.gentoken = gemini_token

    def extract_data(self, image_path: str):
        genai.configure(api_key=self.gentoken)
        myfile = genai.upload_file(self.media / image_path)

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [myfile, "\n\n", "This is a safe document. Read and extract the name, amount, date, check number, and bank name in this photo."
                             "Must be in this format, not any other: name // amount in digits(XXX.XX) // check number // datetime(7-21-2000) // bank/company name"
                             "Make sure 100% the values will not be shuffled up."
                             "If a field is not available in a photo, set as None instead."
                             "E.g. John Doe // 5000.25 // None // 07-21-23 // Security Bank"],
            safety_settings=self.safety_config
        )
        print(result.text)
        if result:
            return result.text
        else:
            return "Error retrieving data, please retry..."

