from typing import List, Dict, Tuple
import math
from src.models.data_models import Component, Pin

class SymbolGenerator:
    """Generates KiCAD symbol files (.kicad_sym) from component data."""

    def __init__(self):
        self.pin_length = 2.54  # mm
        self.text_offset = 0.5
        self.pin_spacing = 2.54
        self.origin_x = 0
        self.origin_y = 0

    def generate_symbol(self, component: Component, pins: List[Pin]) -> str:
        """
        Generates the S-expression string for a KiCAD symbol library.
        
        Args:
            component: The component metadata.
            pins: List of Pin objects.
            
        Returns:
            String containing the .kicad_sym content.
        """
        lib_name = component.part_number
        
        # Header
        content = [
            '(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)',
            f'  (symbol "{lib_name}" (in_bom yes) (on_board yes)',
            f'    (property "Reference" "U" (id 0) (at 0 5 0)',
            '      (effects (font (size 1.27 1.27)))',
            '    )',
            f'    (property "Value" "{lib_name}" (id 1) (at 0 -5 0)',
            '      (effects (font (size 1.27 1.27)))',
            '    )',
            f'    (property "Footprint" "" (id 2) (at 0 -10 0)',
            '      (effects (font (size 1.27 1.27) hide yes))',
            '    )',
            f'    (property "Datasheet" "" (id 3) (at 0 -15 0)',
            '      (effects (font (size 1.27 1.27) hide yes))',
            '    )',
            f'    (property "Description" "{component.description or ""}" (id 4) (at 0 0 0)',
            '      (effects (font (size 1.27 1.27) hide yes))',
            '    )',
            f'    (symbol "{lib_name}_1_1"',
        ]

        # Sort and group pins
        left_pins, right_pins, top_pins, bottom_pins = self._group_pins(pins)
        
        # Calculate body dimensions
        max_vertical_pins = max(len(left_pins), len(right_pins))
        max_horizontal_pins = max(len(top_pins), len(bottom_pins))
        
        height = max(max_vertical_pins * self.pin_spacing + 2.54, 10.16)
        width = max(max_horizontal_pins * self.pin_spacing + 2.54, 10.16)
        
        # Ensure width is wide enough for text (heuristic)
        width = max(width, 15.24)

        half_h = height / 2
        half_w = width / 2
        
        # Draw Rectangle
        content.append(
            f'      (rectangle (start {-half_w} {half_h}) (end {half_w} {-half_h})'
            ' (stroke (width 0.254) (type default) (color 0 0 0 0))'
            ' (fill (type background)))'
        )

        # Place Pins
        content.extend(self._place_pins(left_pins, -half_w, half_h, "left"))
        content.extend(self._place_pins(right_pins, half_w, half_h, "right"))
        content.extend(self._place_pins(top_pins, -half_w, half_h, "top"))
        content.extend(self._place_pins(bottom_pins, -half_w, -half_h, "bottom"))

        content.append('    )') # End symbol_1_1
        content.append('  )')   # End symbol
        content.append(')')     # End lib
        
        return '\n'.join(content)

    def _group_pins(self, pins: List[Pin]) -> Tuple[List[Pin], List[Pin], List[Pin], List[Pin]]:
        left = []
        right = []
        top = []
        bottom = []
        
        for pin in pins:
            etype = (pin.electrical_type or "").lower()
            if "input" in etype or "passive" in etype or "nc" in etype:
                left.append(pin)
            elif "output" in etype or "bidirectional" in etype or "open" in etype:
                right.append(pin)
            elif "power" in etype or "vdd" in etype or "vcc" in etype:
                # Heuristic: Positive power usually VCC, VDD
                if "gnd" in (pin.name or "").lower() or "vss" in (pin.name or "").lower() or "-" in (pin.name or ""):
                    bottom.append(pin)
                else:
                    top.append(pin)
            elif "gnd" in (pin.name or "").lower() or "vss" in (pin.name or "").lower():
                bottom.append(pin)
            else:
                # Default to left if unknown
                left.append(pin)
                
        # Sort by number if possible, otherwise keep order
        def try_int(p):
            try:
                return int(p.number)
            except:
                return 9999
        
        left.sort(key=try_int)
        right.sort(key=try_int)
        top.sort(key=try_int)
        bottom.sort(key=try_int)
        
        return left, right, top, bottom

    def _place_pins(self, pins: List[Pin], x_base: float, y_base: float, side: str) -> List[str]:
        lines = []
        count = len(pins)
        if count == 0:
            return lines

        # Calculate starting position to center pins
        # For vertical sides (left/right), we iterate Y
        # For horizontal sides (top/bottom), we iterate X
        
        if side in ["left", "right"]:
            total_span = (count - 1) * self.pin_spacing
            start_y = total_span / 2
            
            for i, pin in enumerate(pins):
                y = start_y - (i * self.pin_spacing)
                x = x_base
                angle = 0 if side == "right" else 180
                
                # KiCAD pin definition
                # (pin TYPE (at X Y ANGLE) (length L)
                #   (name "NAME" (effects (font (size 1.27 1.27))))
                #   (number "NUM" (effects (font (size 1.27 1.27))))
                # )
                
                kicad_type = self._map_electrical_type(pin.electrical_type)
                
                lines.append(
                    f'      (pin {kicad_type} (at {x} {y} {angle}) (length {self.pin_length})'
                )
                lines.append(
                    f'        (name "{pin.name}" (effects (font (size 1.27 1.27))))'
                )
                lines.append(
                    f'        (number "{pin.number}" (effects (font (size 1.27 1.27))))'
                )
                lines.append('      )')

        elif side in ["top", "bottom"]:
            total_span = (count - 1) * self.pin_spacing
            start_x = -(total_span / 2)
            
            for i, pin in enumerate(pins):
                x = start_x + (i * self.pin_spacing)
                y = y_base
                angle = 270 if side == "top" else 90
                
                kicad_type = self._map_electrical_type(pin.electrical_type)
                
                lines.append(
                    f'      (pin {kicad_type} (at {x} {y} {angle}) (length {self.pin_length})'
                )
                lines.append(
                    f'        (name "{pin.name}" (effects (font (size 1.27 1.27))))'
                )
                lines.append(
                    f'        (number "{pin.number}" (effects (font (size 1.27 1.27))))'
                )
                lines.append('      )')
                
        return lines

    def _map_electrical_type(self, etype: str) -> str:
        if not etype:
            return "passive"
        etype = etype.lower()
        if "input" in etype: return "input"
        if "output" in etype: return "output"
        if "bidirectional" in etype: return "bidirectional"
        if "power" in etype: return "power_in" # Default to power input
        if "passive" in etype: return "passive"
        if "nc" in etype or "no connect" in etype: return "no_connect"
        if "open" in etype: return "open_collector"
        return "passive"
