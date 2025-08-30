// MacroPad RP2040 Case (Bottom and Sides)
// Companion to macropad_top_cover.scad
// Parametric design for Adafruit MacroPad RP2040 keyboard controller
// Author: Generated for CircuitPython EVM Controller project
// License: MIT

// The bottom case along with the filler layer and cover OpenSCAD models provivided
// wraps the Adafruit MacroPad RP2040 in a tightfitting case. The case has a USB port
// the reset button opening, as well as 4 mounting holes to fasten the PCD to the case.
//
// Last update: 08/24/2025
// =============================================================================
// PARAMETERS
// =============================================================================

logotext = "AJAMSONIC HS13+";

// Overall cover dimensions of added Quad Encoder
qencoder_width = 25;      // Width of Quad Encoder (mm)

// Adafruit Macropad RP2040 PCB parameters
pcb_length = 105;          // RP2040 PCB length (mm)
pcb_width = 60 + qencoder_width;    // RP2040 + Quad Encoder PCB width (mm)
pcb_thickness = 1.6;       // Standard PCB thickness (mm)
pcb_clearance = 1;         // Space around PCB (mm)
pcb_height_clearance = 8;  // Space above PCB for components (mm)

// Overall case dimensions (should match top cover)
bottom_thickness = 2;      // Thickness of bottom plate (mm)
wall_thickness = 2;        // Thickness of side walls (mm)
corner_radius = 3;         // Rounded corner radius (mm)
inner_corner_radius = 1;   // Rounded inner corner radius

case_length = pcb_length + (wall_thickness * 2);   // Total length of case (mm)
case_width = pcb_width +  + (wall_thickness * 2);  // Total width of case (mm)
case_height = 14;          // Height of case walls (mm)

// Top cover integration
top_cover_thickness = 3;   // Thickness of top cover (for fit calculation)
top_cover_lip = 1;         // How much top cover overlaps case walls (mm)

// USB port cutout
usb_width = 11;             // Width of USB-C port (mm)
usb_height = 5;            // ** Was 4 - Height of USB-C port (mm)
usb_offset_from_edge = 3;  // Distance from PCB edge to USB center (mm)
usb_position_y = qencoder_width/2 - 3.2; // Y position along case width (0 = center)
usb_corner_radius = 1;     // Rounded corners for USB hole

// PCB mounting holes keep 2mm for wall in mind
mount_hole_diameter = 4.56;   // Diameter for M3 screws (mm)
mount_hole_positions = [   // [X, Y] positions relative to PCB center
    [-pcb_length/2 + 19, -26.5 + qencoder_width/2 - 3.5],   // Bottom left
    [pcb_length/2 - 4, -26.5 + qencoder_width/2 - 3.5],   // Bottom right  
    [-pcb_length/2 + 19, 26.5 + qencoder_width/2 - 3.5],    // Top left
    [pcb_length/2 - 4, 26.5 + qencoder_width/2 - 3.5]     // Top right
];

// Standoffs for PCB mounting
standoff_height = 6;         // Height of PCB standoffs (mm)
standoff_diameter = 5.2;     // Diameter of standoff base (mm)
standoff_hole_diameter = 2.5; // Hole diameter in standoff for screw (mm)

// 3D printing parameters
clearance = 0.2;           // General clearance (mm)
layer_height = 0.2;        // Your 3D printer layer height (mm)

// Catching indent for Cover support lip
cover_lip_indent = [10, 2.5, 2];


// =============================================================================
// MAIN OBJECT
// =============================================================================

difference() {

    union() {
        // Main case body
        case_body();

        // AJAM logo text
        logo_text();
        

        // PCB mounting standoffs
        pcb_standoffs();
    }        

    // Remove internal cavity
    internal_cavity();
        
    // Remove USB port hole
    usb_port_hole();
    
    // Remove Reset port hole
    reset_port_hole();

    // Remove PCB mounting holes
    pcb_mounting_holes();
    
    // Indent in bottom for Stemma connector
    stemma_hole();     
}

// Add cover supports into the case hole
translate([pcb_length/2-4, pcb_width/2-2, 0])   // x and y top
    cube([5, 3, 12]);
translate([-(pcb_length/2+1), pcb_width/2-2, 0])    // -x and y top
    cube([5, 3, 12]);
translate([pcb_length/2-4, -(pcb_width/2+1), 0])    // x and -y bottom
    cube([5, 3, 12]);
// Encoder Support
translate([-(pcb_length/2+1), -(pcb_width/2+1), 0]) // -x and -y bottom
    cube([10, 3, 12 - 3.2]);
translate([10, -(pcb_width/2+1), 0])
    cube([10, 3, 12 - 3.2]);
translate([-5, pcb_width/2-2, 0])   // y top center
    cube([10, 3, 12]);
translate([pcb_length/2-2, -pcb_width/2 + 2, 0])   // x center 
    cube([3, 10, 12]);
translate([-pcb_length/2, -pcb_width/2 + 1, 0])   // quad center 
    cube([3, 10, 12 - 3.2]);
// =============================================================================
// MODULES (Functions)
// =============================================================================

// Create the main case body with walls
module case_body() {
    // Bottom plate
    hull() {
        // Four corner cylinders for rounded rectangle base
        translate([-(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
            cylinder(h = bottom_thickness, r = corner_radius, $fn = 32);
        
        translate([+(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
            cylinder(h = bottom_thickness, r = corner_radius, $fn = 32);
        
        translate([+(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
            cylinder(h = bottom_thickness, r = corner_radius, $fn = 32);
        
        translate([-(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
            cylinder(h = bottom_thickness, r = corner_radius, $fn = 32);
    }
    
    // Side walls
    difference() {
        // Outer wall
        hull() {
            translate([-(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
                cylinder(h = case_height, r = corner_radius, $fn = 32);
            
            translate([+(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
                cylinder(h = case_height, r = corner_radius, $fn = 32);
            
            translate([+(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
                cylinder(h = case_height, r = corner_radius, $fn = 32);
            
            translate([-(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
                cylinder(h = case_height, r = corner_radius, $fn = 32);
        }
        
        // Inner cavity (removed in main difference)
        translate([0, 0, bottom_thickness])
            hull() {
                inner_radius = corner_radius - wall_thickness;
                inner_length = case_length - 2 * wall_thickness;
                inner_width = case_width - 2 * wall_thickness;
                
                translate([-(inner_length/2 - inner_radius), -(inner_width/2 - inner_radius), 0])
                    cylinder(h = case_height, r = inner_radius, $fn = 32);
                
                translate([+(inner_length/2 - inner_radius), -(inner_width/2 - inner_radius), 0])
                    cylinder(h = case_height, r = inner_radius, $fn = 32);
                
                translate([+(inner_length/2 - inner_radius), +(inner_width/2 - inner_radius), 0])
                    cylinder(h = case_height, r = inner_radius, $fn = 32);
                
                translate([-(inner_length/2 - inner_radius), +(inner_width/2 - inner_radius), 0])
                    cylinder(h = case_height, r = inner_radius, $fn = 32);
            }
    }
    
    // Top cover lip/ledge
    translate([0, 0, case_height - top_cover_thickness]) {
        difference() {
            // Outer ledge
            hull() {
                translate([-(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
                    cylinder(h = top_cover_thickness, r = corner_radius, $fn = 32);
                
                translate([+(case_length/2 - corner_radius), -(case_width/2 - corner_radius), 0])
                    cylinder(h = top_cover_thickness, r = corner_radius, $fn = 32);
                
                translate([+(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
                    cylinder(h = top_cover_thickness, r = corner_radius, $fn = 32);
                
                translate([-(case_length/2 - corner_radius), +(case_width/2 - corner_radius), 0])
                    cylinder(h = top_cover_thickness, r = corner_radius, $fn = 32);
            }
            
            // Inner cutout for top cover
            hull() {
                ledge_radius = corner_radius - top_cover_lip;
                ledge_length = case_length - 2 * top_cover_lip;
                ledge_width = case_width - 2 * top_cover_lip;
                
                translate([-(ledge_length/2 - ledge_radius), -(ledge_width/2 - ledge_radius), -0.5])
                    cylinder(h = top_cover_thickness + 1, r = ledge_radius, $fn = 32);
                
                translate([+(ledge_length/2 - ledge_radius), -(ledge_width/2 - ledge_radius), -0.5])
                    cylinder(h = top_cover_thickness + 1, r = ledge_radius, $fn = 32);
                
                translate([+(ledge_length/2 - ledge_radius), +(ledge_width/2 - ledge_radius), -0.5])
                    cylinder(h = top_cover_thickness + 1, r = ledge_radius, $fn = 32);
                
                translate([-(ledge_length/2 - ledge_radius), +(ledge_width/2 - ledge_radius), -0.5])
                    cylinder(h = top_cover_thickness + 1, r = ledge_radius, $fn = 32);
            }
        }
    }
}

// Create internal cavity (removed from main body)
module internal_cavity() {
    translate([0, 0, bottom_thickness]) {
        inner_radius = inner_corner_radius;
        inner_length = case_length - 2 * wall_thickness;
        inner_width = case_width - 2 * wall_thickness;

        hull() {
            translate([-(inner_length/2 - inner_radius), -(inner_width/2 - inner_radius), 0])
                cylinder(h = case_height, r = inner_radius, $fn = 32);
            
            translate([+(inner_length/2 - inner_radius), -(inner_width/2 - inner_radius), 0])
                cylinder(h = case_height, r = inner_radius, $fn = 32);
            
            translate([+(inner_length/2 - inner_radius), +(inner_width/2 - inner_radius), 0])
                cylinder(h = case_height, r = inner_radius, $fn = 32);
            
            translate([-(inner_length/2 - inner_radius), +(inner_width/2 - inner_radius), 0])
                cylinder(h = case_height, r = inner_radius, $fn = 32);
        }
    }
}

// Create Logo lettering on the right side
module logo_text() {
    wall_offset = (pcb_width + (wall_thickness * 2)) / 2;
    
    translate([0, -wall_offset + 0.5, 7]) // y = -31.5
    rotate([90,0,0]) {
        cube([70, 10, 1], center = true);
        font = "DejaVu Sans:style=Bold";
        letter_size = 5;
        string = logotext;
        linear_extrude(height = 0.8) {
          text(string, size = letter_size, font = font, halign = "center", valign = "center");
        }
    }
}

// Indent for the Quad Encoder Stemma connector & cable in the base
module stemma_hole() {
    translate([20, -35, 0.5])
        cube([10, 10, 10]);
}

// Create PCB mounting standoffs
module pcb_standoffs() {
    for (pos = mount_hole_positions) {
        translate([pos[0], pos[1], bottom_thickness]) {
            cylinder(
                h = standoff_height, 
                d = standoff_diameter, 
                $fn = 16
            );
        }
    }
}

// Create USB port hole
module usb_port_hole() {
    // Position USB hole on the side wall
    translate([
        (case_length/2 - usb_offset_from_edge), 
        usb_position_y, 
        bottom_thickness + standoff_height + pcb_thickness + usb_height/2 - 5.5
    ]) {
        rotate([0, 90, 0]) {
            // Rounded rectangle for USB port
            hull() {
                translate([-(usb_height/2 - usb_corner_radius), -(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([+(usb_height/2 - usb_corner_radius), -(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([+(usb_height/2 - usb_corner_radius), +(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([-(usb_height/2 - usb_corner_radius), +(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
            }
        }
    }
}

// Create Reset port hole
module reset_port_hole() {
    
    echo(pcb_length/2 - 22.5 + qencoder_width/2- 3.2);
    
    // Position Reset hole on the side wall
    translate([
        -usb_position_y + (pcb_length/2 - 22.5 + qencoder_width/2- 3.2),  //22.5
        (case_width/2 + usb_offset_from_edge - 1), 
        bottom_thickness + standoff_height + pcb_thickness + usb_height/2 - 5
    ]) {
        rotate([0, 90, 0]) {
            // Rounded rectangle for Reset port
            hull() {
                translate([-(usb_height/2 - usb_corner_radius), -(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([+(usb_height/2 - usb_corner_radius), -(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([+(usb_height/2 - usb_corner_radius), +(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
                
                translate([-(usb_height/2 - usb_corner_radius), +(usb_width/2 - usb_corner_radius), 0])
                    cylinder(h = wall_thickness + 2, r = usb_corner_radius, $fn = 16);
            }
        }
    }
}

// Create PCB mounting holes
module pcb_mounting_holes() {
    for (pos = mount_hole_positions) {
        color("blue") translate([pos[0], pos[1], -0.5]) {
            // Through hole for screw
            cylinder(
                h = bottom_thickness + 1, 
                d = mount_hole_diameter + clearance, 
                $fn = 16
            );
        }
            
        // Countersink hole in standoff
        color("red") translate([pos[0], pos[1], -0.5]) {
            cylinder(
                h = bottom_thickness - 0.5, 
                d = mount_hole_diameter + clearance + 2, 
                $fn = 16
            );
        }
    }
}

