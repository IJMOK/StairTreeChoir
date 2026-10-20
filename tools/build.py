"""Regenerate every generated file: python -m tools.build"""

from tools import gen_cnc, gen_xmodel, tree_layout


def main() -> None:
    tree_layout.main()
    gen_cnc.main()
    gen_xmodel.main()


if __name__ == "__main__":
    main()
