"""Regenerate every generated file: python -m tools.build"""

from tools import gen_cnc, gen_controller, gen_site_wiring, gen_xmodel, tree_layout


def main() -> None:
    tree_layout.main()
    gen_cnc.main()
    gen_xmodel.main()
    gen_controller.main()
    gen_site_wiring.main()


if __name__ == "__main__":
    main()
