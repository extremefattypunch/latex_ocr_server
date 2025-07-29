import argparse
import logging
from .__about__ import __version__

def run():
    logging.basicConfig()
    args = parse_option()
    args.func(args)

# latex_ocr_server info ...
def handle_info(args):
    if args.gpu_available:
        import torch

        is_available = torch.cuda.is_available()
        print(f"{is_available}")
        exit(not is_available)

# latex_ocr_server start ...
def handle_start(args):
    from .server import serve
    serve(args.port, args.cpu)
        
def parse_option():
    parser = argparse.ArgumentParser(prog="latex_ocr_server", description="A server that translates paths to images of equations to latex using protocol buffers.")
    parser.add_argument("--version", action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(help='sub-command help', required=True)
    start = subparsers.add_parser("start", help='start the server')
    start.add_argument("--port", default="50051")
    start.add_argument("--cpu", default=False, action="store_true", help="use cpu, otherwise uses gpu if available")
    start.set_defaults(func=handle_start)

    info = subparsers.add_parser("info", help="get server info")
    info.add_argument("--gpu-available", required=True, action="store_true", help="check if gpu support is enabled")    
    info.set_defaults(func=handle_info)

    return parser.parse_args()

if __name__ == "__main__":
    run()
