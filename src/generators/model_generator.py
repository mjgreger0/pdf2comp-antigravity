import os
from typing import Dict, Any, Optional
from src.models.data_models import Package

try:
    import cadquery as cq
    HAS_CQ = True
except ImportError:
    HAS_CQ = False

class ModelGenerator:
    """Generates 3D models (.step, .wrl) using CadQuery."""

    def __init__(self):
        pass

    def generate_model(self, package: Package, output_dir: str) -> bool:
        """
        Generates STEP and WRL models for the package.
        
        Args:
            package: The package metadata.
            output_dir: Directory to save the models.
            
        Returns:
            True if successful, False otherwise.
        """
        if not HAS_CQ:
            print("Warning: CadQuery not installed. Skipping 3D model generation.")
            return False

        name = package.name
        dims = package.dimensions or {}
        pkg_type = (package.package_type or "").lower()
        
        try:
            model = None
            
            if "qfn" in pkg_type:
                model = self._make_qfn(dims)
            elif "soic" in pkg_type or "sop" in pkg_type:
                model = self._make_soic(dims)
            else:
                # Default to a simple box
                model = self._make_box(dims)
                
            if model:
                # Ensure output directory exists
                os.makedirs(output_dir, exist_ok=True)
                
                step_path = os.path.join(output_dir, f"{name}.step")
                # wrl_path = os.path.join(output_dir, f"{name}.wrl")
                
                # Export STEP
                cq.exporters.export(model, step_path)
                
                # Export WRL (CadQuery support for WRL is limited/experimental in some versions, 
                # but usually we export STEP for KiCAD mechanical and WRL for visual if needed.
                # KiCAD can use STEP directly for 3D view now.)
                # For now, we just export STEP as it's the most important.
                
                return True
                
        except Exception as e:
            print(f"Error generating model for {name}: {e}")
            return False
            
        return False

    def _make_box(self, dims: Dict[str, float]) -> Any:
        w = dims.get("body_width", 5.0)
        l = dims.get("body_length", 5.0)
        h = dims.get("height", 1.0)
        
        return cq.Workplane("XY").box(l, w, h)

    def _make_qfn(self, dims: Dict[str, float]) -> Any:
        # Simplified QFN
        body_w = dims.get("body_width", 5.0)
        body_l = dims.get("body_length", 5.0)
        height = dims.get("height", 0.8)
        
        # Body with Pin 1 mark
        # We start with the box, select the top face (>Z), create a workplane,
        # move to the corner, draw a circle, and cut it into the body.
        result = (
            cq.Workplane("XY")
            .box(body_l, body_w, height)
            .faces(">Z")
            .workplane()
            .moveTo(-body_l/2 + 0.5, body_w/2 - 0.5)
            .circle(0.2)
            .cutBlind(-0.1)
        )
        
        return result

    def _make_soic(self, dims: Dict[str, float]) -> Any:
        # Simplified SOIC
        body_w = dims.get("body_width", 4.0)
        body_l = dims.get("body_length", 5.0)
        height = dims.get("height", 1.5)
        
        body = cq.Workplane("XY").box(body_l, body_w, height)
        
        # Legs would be added here in a full implementation
        # For now, just the body
        
        return body
