import re
from .protos import latex_ocr_pb2_grpc
from .protos import latex_ocr_pb2
import grpc
from PIL import Image
import torch
from concurrent import futures
from surya.recognition import RecognitionPredictor
from surya.common.surya.schema import TaskNames
from markdownify import markdownify
from bs4 import BeautifulSoup

class LatexOCR(latex_ocr_pb2_grpc.LatexOCRServicer):
    def __init__(self, device):
        self.device = device
        self.predictor = RecognitionPredictor()  # Initialize RecognitionPredictor directly
        print("Server started")

    def GenerateLatex(self, request, context):
        try:
            image = Image.open(request.image_path)
            if not image.mode == "RGB":
                image = image.convert('RGB')
            result = self.inference(image)
            return latex_ocr_pb2.LatexReply(latex=result)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing image: {str(e)}")
            return latex_ocr_pb2.LatexReply()

    def IsReady(self, request, context):
        return latex_ocr_pb2.ServerIsReadyReply(is_ready=True)  # Always ready since no async loading

    def GetConfig(self, request, context):
        return latex_ocr_pb2.ServerConfig(device=str(self.device))

    def inference(self, image):
        tasks = [TaskNames.block_without_boxes]  # Task for processing the entire image
        bboxes = [[[0, 0, image.width, image.height]]]  # Bounding box for the full image
        predictions = self.predictor([image], tasks, bboxes=bboxes)
        if predictions and predictions[0].text_lines:
            text = predictions[0].text_lines[0].text  # Extract LaTeX from the first text line
# Parse HTML with BeautifulSoup

            soup = BeautifulSoup(text, 'html.parser')

# Process <math> tags
            for math_tag in soup.find_all('math'):
                display = math_tag.get('display', 'inline')
                latex = math_tag.get_text()
                # Clean LaTeX by replacing double backslashes with single backslashes
                replacement = f'<math>\n$${latex}$$\n</math>' if display == 'block' else f'<math>${latex}$</math>'
                math_tag.replace_with(replacement)

# Convert modified HTML to string
            modified_text = str(soup)
            modified_texT=modified_text.split("\\n")
            modified_text="".join(modified_texT)
# Convert to Markdown
            markdown_text = markdownify(modified_text,strip=['math'],escape_astericks=False,escape_underscores=False,escape_misc=False,heading_style="ATX",newline_style="SPACES")
            markdown_text=markdown_text.replace("<math>","")
            markdown_text=markdown_text.replace("</math>","")
            latex = markdown_text
        else:
            latex = ""  # Handle case where no text lines are found
        return latex

def serve(port: str, cpu: bool):
    if not cpu and torch.cuda.is_available():
        device = torch.device("cuda:0")
    else:
        device = torch.device("cpu")
    print(f"Starting server on port {port}, using {device}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    latex_ocr_pb2_grpc.add_LatexOCRServicer_to_server(LatexOCR(device), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()
