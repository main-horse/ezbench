import json
import PIL.Image
from google import genai
from google.genai import types

# contents="Explain how AI works in a few words"

# image = PIL.Image.open('/path/to/image.png')
# contents=["What is this image?", image])

# image = requests.get(image_path)
# contents=["What is this image?", types.Part.from_bytes(data=image.content, mime_type="image/jpeg")])

class GenAIModel:
    def __init__(self, name):
        self.name = name
        config = json.load(open("config.json"))
        self.hparams = config['hparams']
        self.client = genai.Client(api_key=config['llms']['genai']['api_key'])

    def make_request(self, conversation: list[str], add_image: PIL.Image.Image | None=None, max_tokens=2048, stream=False):
        if add_image is not None: conversation = conversation + [add_image]
        response = self.client.models.generate_content(
            model=self.name, contents = conversation, config=types.GenerateContentConfig(max_output_tokens=max_tokens)
        )
        try: return response.text
        except: return ''*bool(__import__("traceback").print_exc())
        

if __name__ == "__main__":
    import sys
    #q = sys.stdin.read().strip()
    q = "why?"
    print(VertexAIModel("gemini-1.5-pro-preview-0409").make_request(["hi, how are you doing", "i'm a bit sad", q]))
