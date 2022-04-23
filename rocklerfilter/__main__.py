"""wrapper to run the CLI or the GUI version of the application"""
import argparse
import rockler_cli, rockler_gui
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--gui", action="store_true", help="launch gui app")
parser.add_argument("-c", "--cli", action="store_true", help="launch command line app")
args = parser.parse_args()
if args.gui:
    rockler_gui.main()
else:
    rockler_cli.main()
