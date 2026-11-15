"""Regenerate the generated files: python -m tools.build (make all). The printed parts and the
assembly come from the FreeCAD masters: python -m tools.cad (make cad), a few minutes."""

from tools import (cad, gen_cnc, gen_controller, gen_docs_site, gen_site_config, gen_site_wiring, gen_tree_wiring,
                   gen_xmodel, tree_layout)


def main() -> None:
    tree_layout.main()
    gen_cnc.main()
    # The tread's CAM files (FreeCAD, ~30s). The rest of the CAD is `make cad` (python -m tools.cad).
    if cad.freecadcmd():
        if cad.run(("tree",)):
            raise SystemExit("the FreeCAD tree export failed")
    else:
        print("skipped cad/stair-tree.*: freecadcmd not found (FreeCAD 1.1)")
    gen_xmodel.main()
    gen_controller.main()
    gen_site_wiring.main()
    gen_site_config.main()
    gen_tree_wiring.main()
    gen_docs_site.main()


if __name__ == "__main__":
    main()
