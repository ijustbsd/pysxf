import sqlite3

from pysxf import SXF


def main():
    sxf = SXF('n-37-141.sxf')
    print(sxf)

    sxf.parse()


if __name__ == '__main__':
    main()
