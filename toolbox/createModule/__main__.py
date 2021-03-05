from createModule import createModule
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a template module.')
    parser.add_argument('nameCamel', help='module name in camelCase')
    parser.add_argument('-d', '--creationDir', default='.', type=os.path.abspath, help='relative creation directory')
    parser.add_argument('-m', '--createMain', nargs='?', const=True, default=False,
                        help='whether to create main file')
    args = parser.parse_args()
    createModule(args.nameCamel, args.creationDir, createMain=args.createMain)
