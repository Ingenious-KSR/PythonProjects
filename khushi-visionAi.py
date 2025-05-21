# import vertexai,os,json
# from google.oauth2 import service_account
# from google.cloud import aiplatform
# from vertexai.generative_models import GenerativeModel, Part

# # Path to your JSON key file
# key_path = r"D:\ProgramData\PythonProjects\reliable-airway-443501-e6-d1555c142b52.json"

# # Load credentials from the JSON key file
# credentials = service_account.Credentials.from_service_account_file(key_path)


# PROJECT_ID = "reliable-airway-443501-e6"
# vertexai.init(project=PROJECT_ID, location="us-central1",credentials=credentials)

# model = GenerativeModel("gemini-1.5-pro-001") #flash-002

# #local_image_path = r"D:\Gemini\Input_LabCorp1_71_6_textual-page.1.png"
# local_image_path = r"D:\ProgramData\PythonProjects\WhatsApp Image 2025-01-28 at 12.24.40_06ebf264.jpg"
# file_type = "image/png"
# # Read the local image as binary data
# with open(local_image_path, "rb") as image_file:
#     image_data = image_file.read()

# prompt ="""Analyze this medical lab report image as a clinical informatics expert and data scientist. Extract blood biomarker data into JSON format with these specifications:

#             TARGET FORMAT:
#             {
#                 "Results": [
#                     {
#                         "Date": "", 
#                         "Biomarker-Name": "",
#                         "Result": "",
#                         "Low-Ref-Range": "",
#                         "High-Ref-Range": "",
#                         "Unit-of-measurement": "",
#                         "Comment": ""
#                     }
#                 ]
#             }

#             EXTRACTION RULES:
#             1. Find all blood biomarkers:
#             - Include all blood biomarkers present
#             - Keep original biomarker names including spaces/brackets
#             - Exclude non-blood biomarker data

#             2. Handle multiple results:
#             - Create separate JSON entries for each result of the same biomarker
#             - Include all historical/previous results
#             - Preserve date for each result when available

#             3. Process reference ranges:
#             - For ranges with "-": Split into Low and High
#             - For "<" values: Put in Low-Ref-Range
#             - For ">" values: Put in High-Ref-Range
#             - For multiple ranges: Use optimal/desirable range and add others in Comment

#             4. Handle units:
#             - Use provided unit of measurement
#             - For ratios without units, use "Ratio"
#             - For multiple units, convert to SI unit
#             - Do not include units in Result or Ref-Range fields

#             5. Date formatting:
#             - Convert all dates to DD/MM/YYYY
#             - Leave blank if no date

#             6. Additional requirements:
#             - Keep original numeric values (no recalculations)
#             - Remove stop words and irrelevant symbols
#             - Handle non-English characters appropriately
#             - Include all fields in JSON even if empty

#             Return only the structured JSON without additional commentary."""

# response = model.generate_content(
#     [
#         Part.from_data(image_data, mime_type=file_type), #"application/pdf"), #image/jpg
#         prompt,
#     ]
# )

# # Write the response text to a file
# FILE_NAME = os.path.splitext(os.path.basename(local_image_path))[0]
# output_file_path = os.path.join(r"E:\JondaX internship\Testing files\Result", FILE_NAME + "Json.txt")   # Specify the output file path
#     #D:\Gemini\OutputDocAi
# if response.candidates:
#     text = response.text
#     #print(repr(text))
#     # Debug: Print the raw response content
#     print("Raw response content:", text)
#     #if text.startswith("json") and text.endswith(""):
#         #text = text[7:-3].strip()  # Remove json and    
#     text = text.replace("json", "").replace("", "").strip()
#     #print("Stripped response content:", text)
#     # Parse the response content as JSON
#     try:
#         jsonObj = json.loads(text)
#         #print("Parsed JSON:", jsonObj)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing JSON: {e}")
#         #print(f"Response content: {response.text}")
#         jsonObj = None  # Set a default value or handle the error
# else:
#     print("No candidates found in the response.")
#     jsonObj = None

# with open(output_file_path, "w", encoding="utf-8") as output_file:
#     output_file.write(text)
# #print(text)
# print(f"Response saved to: {output_file_path}")

# Results = jsonObj["Results"]

# # Process each result in the JSON response
# globalResultIndex=0
# textRaw =''
# for resultIndex, result in enumerate(Results):
#     globalResultIndex += 1
    
#     # Extract result details
#     testName = '' 
#     testValue = '' 
#     testUnit = '' 
#     testLoRange = '' 
#     testHiRange = '' 
#     testDate = ''
#     testName = result["Biomarker-Name"]
#     testValue = result["Result"]
#     try: 
#         testUnit = result["Unit-of-measurement"]
#     except: testUnit=''
#     try: 
#         testLoRange = result["Low-Ref-Range"]
#     except: testLoRange=''
#     try: 
#         testHiRange = result["High-Ref-Range"]
#     except: testHiRange=''
#     try: 
#         testDate = result["Date"]
#     except: testDate=''
    
#     print(globalResultIndex, testName, testValue, testUnit, testLoRange, testHiRange, testDate)
    
#     #Khushi's code
#     textRaw =textRaw+ str(globalResultIndex)+"\t"+str(testName)+"\t"+"\t"+str(testValue)+"\t"+ str(testUnit)+"\t"+ str(testLoRange)+"\t"+str(testHiRange)+"\t"+str(testDate)+"\n"
    
#     print(globalResultIndex, testName, testValue, testUnit, testLoRange, testHiRange, testDate)
    
# output_file_path_raw = os.path.join(r"E:\JondaX internship\Testing files\Result", FILE_NAME + "Raw.txt")
# with open(output_file_path_raw, "w", encoding="utf-8") as output_file:
#     output_file.write(textRaw)
# print(f"Raw text saved to: {output_file_path_raw}")
#     #khushi code ends here
    
#     # Save extracted information to Globals by calling IrisClassMethod
#     #iris.cls("python.VertexAi").SaveToGlobalAIDATA(rid, globalResultIndex, testName, testValue, testUnit, testLoRange, testHiRange, testDate )




# Import necessary libraries
import io
import os

from google.cloud import vision

# Replace with your GCP project ID
project_id = "your-project-id"

# Function to extract text from an image using Vision API
def extract_text(image_path):
    """Extracts text from an image using Google Cloud Vision API.

    Args:
        image_path: Path to the image file.

    Returns:
        A string containing the extracted text.
    """

    client = vision.ImageAnnotatorClient(client_options={"project": project_id})

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Extract text with document understanding features
    response = client.text_detection(image=image, features=[vision.Feature.DOCUMENT_TEXT_DETECTION])

    full_text = ""
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    symbols = "".join(symbol.text for symbol in word.symbols)
                    full_text += symbols + " "
    return full_text

# Local path to your image file
image_path = r"D:\ProgramData\PythonProjects\WhatsApp Image 2025-01-28 at 12.24.40_06ebf264.jpg"

# Extract text from the image
text = extract_text(image_path)

# Print the extracted text for further processing
print("Extracted Text:", text)

# Further process the extracted text to parse relevant lab results (logic not included here)
# This might involve regular expressions or custom parsing libraries