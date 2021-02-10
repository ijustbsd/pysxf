from pysxf import SXF


def main():
    sxf = SXF('n-37-141.sxf', rsc_path='100t03g.rsc')
    sxf.parse()

    for obj in sxf.objects:
        rsc_obj = sxf.rsc.objects[obj.class_code]
        prim = sxf.rsc.display_params[rsc_obj.internal_code]


if __name__ == '__main__':
    main()
