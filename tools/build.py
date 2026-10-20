"""Regenerate every generated file: python -m tools.build"""

from tools import gen_cnc, tree_layout


def main() -> None:
    tree_layout.main()
    gen_cnc.main()


if __name__ == "__main__":
    main()
