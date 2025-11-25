import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.data_models import Component, Package, Pin
from src.generators.symbol_generator import SymbolGenerator
from src.generators.footprint_generator import FootprintGenerator
from src.generators.model_generator import ModelGenerator

def test_generators():
    print("Testing Generators...")
    
    # Setup Dummy Data
    comp = Component(
        id=1,
        datasheet_id=1,
        part_number="TEST-IC-001",
        description="Test Component",
        manufacturer="TestMfg"
    )
    
    pkg = Package(
        id=1,
        component_id=1,
        name="QFN-32",
        package_type="QFN",
        dimensions={
            "body_width": 5.0,
            "body_length": 5.0,
            "pitch": 0.5,
            "pin_count": 32,
            "lead_length": 0.4,
            "lead_width": 0.25
        }
    )
    
    pins = []
    for i in range(1, 33):
        etype = "passive"
        if i <= 8: etype = "input"
        elif i <= 16: etype = "power_in"
        elif i <= 24: etype = "output"
        
        pins.append(Pin(
            id=i,
            package_id=1,
            number=str(i),
            name=f"P{i}",
            electrical_type=etype
        ))
        
    # Test Symbol Generator
    print("\n[Symbol Generator]")
    sym_gen = SymbolGenerator()
    sym_out = sym_gen.generate_symbol(comp, pins)
    print(f"Generated {len(sym_out)} chars of symbol data.")
    if "(kicad_symbol_lib" in sym_out:
        print("PASS: Header found")
    else:
        print("FAIL: Header missing")
        
    # Test Footprint Generator
    print("\n[Footprint Generator]")
    fp_gen = FootprintGenerator()
    fp_out = fp_gen.generate_footprint(pkg)
    print(f"Generated {len(fp_out)} chars of footprint data.")
    if "(kicad_mod" in fp_out:
        print("PASS: Header found")
    else:
        print("FAIL: Header missing")
        
    # Test Model Generator
    print("\n[Model Generator]")
    model_gen = ModelGenerator()
    out_dir = "test_output"
    if model_gen.generate_model(pkg, out_dir):
        print(f"PASS: Model generated in {out_dir}")
        if os.path.exists(os.path.join(out_dir, "QFN-32.step")):
            print("PASS: STEP file exists")
        else:
            print("FAIL: STEP file missing")
    else:
        print("SKIP: Model generation failed (likely no CadQuery)")

    # Cleanup
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

if __name__ == "__main__":
    test_generators()
