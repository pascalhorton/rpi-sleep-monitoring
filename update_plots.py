import shutil
import sys
import os
import glob
from pathlib import Path
from plot_night import create_plot


def main():
    if len(sys.argv) < 4:
        print('Usage: {} input_dir plot_dir nb_files'.format(sys.argv[0]))
        sys.exit(1)

    input_dir = sys.argv[1]
    plot_dir = sys.argv[2]
    nb_files = int(sys.argv[3])

    Path(plot_dir + '/csv_files').mkdir(parents=True, exist_ok=True)

    csv_files = glob.glob("{}/*.csv".format(input_dir))
    csv_files.sort(reverse=True)
    if len(csv_files) > nb_files:
        del csv_files[0:-nb_files]

    for file in csv_files:
        if not plot_already_updated(file):
            create_plot(file, plot_dir)
            shutil.copyfile(file, '{}/{}/{}'.format(plot_dir, 'csv_files', os.path.basename(file)))


if __name__ == '__main__':
    main()
