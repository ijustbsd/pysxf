from pysxf import SXF


def main():
    sxf = SXF('n-37-141.sxf', rsc_path='100t03g.rsc')
    sxf.parse()

    for obj in sxf.objects[:1]:
        print(obj, end='\n\n')
        rsc_objs = sxf.rsc.objects[obj.class_code]
        for prim in rsc_objs:
            print(prim, end='\n\n')


if __name__ == '__main__':
    main()
