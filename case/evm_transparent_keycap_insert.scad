// Modified keycap based on the imported STL file below to be used with EVM Arranger


rotate([180, 0, 0])
translate([0, 0, -4.5])
union() {
    
    // Import reference file
    translate([-19, 0, -1]) {
        import("C:/Users/a_min/Ketron-EVM-Button-Controller/case/transparent_keycap_insert.stl");
    }
    
    // Add a few inserts to prevent spotty LED shine through top cover
    color("red")
    translate([-6.5, -6.5, 3.25])
        cube([4.5, 3.5, 0.4]);

    color("red")
    translate([2, -6.5, 3.25])
        cube([4.5, 3.5, 0.4]);

    //color("red")
    //translate([-6, 3, 3.25])
    //    cube([4 , 3, 0.4]);

    //color("red")
    //translate([2, 3, 3.25])
    //    cube([4 , 3, 0.4]);

    difference() {
        translate([-7.4, -7.4, -2.25]) {
            cube([14.75, 14.75, 2]);
        }

        translate([-6.5, 1-7.5, -2.5])
            cube([13, 13, 3]);
    }
}