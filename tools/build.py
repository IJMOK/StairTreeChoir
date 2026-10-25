"""Regenerate every generated file: python -m tools.build"""

from tools import gen_cnc, gen_controller, gen_site_config, gen_site_wiring, gen_xmodel, tree_layout


def main() -> None:
    tree_layout.main()
    gen_cnc.main()
    try:
        from tools import gen_step
    except ImportError:
        print("skipped cad/*.step: CadQuery not installed (pip install -r requirements-cad.txt)")
    else:
        gen_step.main()
    gen_xmodel.main()
    gen_controller.main()
    gen_site_wiring.main()
    gen_site_config.main()


if __name__ == "__main__":
    main()
