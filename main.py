import argparse
from dotenv import load_dotenv
from src.forecast import run

parser = argparse.ArgumentParser(
    prog='forecast_timeseries',
    description='forecast_timeseries',
)
parser.add_argument(
    "-d",
    "--dev",
    action="store_true",
    help='Run the progam in development mode.',
)


load_dotenv()


if __name__ == "__main__":
    args = parser.parse_args()
    if args.dev:
        print("hello world!")
    else:
        print("Production mode.")
        run()
