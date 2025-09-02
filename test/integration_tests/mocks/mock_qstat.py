from optparse import OptionParser

parser = OptionParser()
parser.add_option(
    "-q",
    "--register",
    action="store_true",
    dest="register",
    default=False,
    help="Process and add all calculations contained in the current directory and all its subdirectories to known_jobs.dat",
)  # working


def main():
    print("mock_file")


if __name__ == "__main__":
    main()
