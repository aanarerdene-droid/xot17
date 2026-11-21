// Reverse vending machine concept for PET bottle collection
// Units: millimetres. Front is the negative Y face; floor is Z=0.
// Open in OpenSCAD to edit the concept. Use the color 3MF for Fusion; STL is monochrome.
$fn = 48;

machine_width = 760;
machine_depth = 700;
machine_height = 1850;
case_color = [0.88, 0.90, 0.91];
accent_color = [0.04, 0.48, 0.39];
dark_color = [0.10, 0.13, 0.14];

module block(x,y,z,w,d,h,c) {
    color(c) translate([x,y,z]) cube([w,d,h], center=true);
}

module front_cylinder(x,y,z,r,h,c) {
    color(c) translate([x,y,z]) rotate([90,0,0]) cylinder(r=r,h=h,center=true);
}


// QR payload is the demo machine identifier LW-024. The live app/backend URL
// can replace this payload when a hosted pairing service is available.
qr_rows = [
    "111111100010101111111",
    "100000100000101000001",
    "101110101010001011101",
    "101110100000101011101",
    "101110100101101011101",
    "100000100111001000001",
    "111111101010101111111",
    "000000001010000000000",
    "111011111010111000100",
    "001000000001010100000",
    "011000111111011101011",
    "100010010001110111010",
    "111111110101011100010",
    "000000001110001100110",
    "111111101100100011111",
    "100000101100001101011",
    "101110101010101111011",
    "101110100111010011010",
    "101110101111011010101",
    "100000101101110111010",
    "111111101011011011011"
];
module qr_badge() {
    block(-200,-360,1105,148,20,164,accent_color);
    block(-200,-372,1105,116,4,116,[1,1,1]);
    for (r=[0:20], c=[0:20]) {
        if (qr_rows[r][c] == "1")
            block(-200-42+c*4,-376,1105+42-r*4,4,2.96,4,dark_color);
    }
    block(-200,-372,1032,132,6,13,[0.94,0.97,0.93]);
    color([0.04,0.18,0.13]) translate([-200,-378,1028]) rotate([90,0,0])
        linear_extrude(height=1) text("SCAN TO CONNECT", size=7, halign="center");
}

// Main cabinet and kick plate
block(0,0,925, machine_width,machine_depth,1750, case_color);
block(0,-12,55, machine_width+20,machine_depth+10,110, accent_color);
// Rounded-looking header cap and brand band
block(0,-4,1805, machine_width+12,machine_depth+14,90, accent_color);
block(0,-358,1802, 390,12,54, [0.96,0.98,0.96]);
// Brand badge and PET return wording as a clear raised marker
block(-8,-366,1802, 14,5,30, accent_color);
qr_badge();

// User interface: screen, bezel, and three tactile controls
block(-205,-354,1455, 270,24,205, dark_color);
block(-205,-369,1455, 232,8,164, [0.12,0.27,0.29]);
block(-205,-375,1385, 154,5,7, [0.32,0.80,0.66]);
front_cylinder(-205,-371,1300, 24,16, accent_color);
front_cylinder(-145,-371,1300, 15,16, [0.91,0.69,0.18]);

// Bottle intake with raised safety surround and dark throat
block(170,-354,1410, 350,30,300, accent_color);
block(170,-373,1410, 300,10,240, dark_color);
block(170,-381,1437, 252,6,110, [0.025,0.035,0.04]);
// Scan lens and status light
front_cylinder(294,-380,1530, 13,9, [0.33,0.82,0.99]);
front_cylinder(48,-380,1530, 10,9, [0.91,0.69,0.18]);

// Lower transparent collection-bin window and access door outline
block(0,-354,660, 560,20,555, dark_color);
block(0,-368,660, 520,8,515, [0.64,0.83,0.80]);
// Interior stack of simple PET bottle silhouettes visible through the window
for (x=[-180,-95,0,95,180]) {
    color([0.55,0.76,0.69,0.85])
      translate([x,-377,540]) rotate([90,0,0]) cylinder(h=6,r=34,center=true);
    color([0.55,0.76,0.69,0.85])
      translate([x,-377,585]) rotate([90,0,0]) cylinder(h=6,r1=22,r2=34,center=true);
    color([0.55,0.76,0.69,0.85])
      translate([x,-377,620]) rotate([90,0,0]) cylinder(h=6,r=16,center=true);
}
// Door seam, handle, and bin-full indicator
block(306,-356,660, 4,10,590, dark_color);
block(271,-373,680, 18,18,92, accent_color);
front_cylinder(0,-374,960, 13,8, [0.91,0.69,0.18]);

// Side ventilation louvers (visible from either side)
for (z=[210:38:438]) {
    block(0,-351,z, 220,8,10, dark_color);
}

// Four low-profile feet
for (x=[-300,300], y=[-250,250]) {
    color(dark_color) translate([x,y,18]) cylinder(r=38,h=36,center=true);
}

// Small PET recycling emblem: three raised arrows simplified to triangular fins
for (a=[0,120,240]) {
    color([0.96,0.98,0.96]) translate([0,-369,1680]) rotate([0,0,a])
      linear_extrude(height=4) polygon(points=[[0,58],[17,28],[7,28],[7,-26],[-7,-26],[-7,28],[-17,28]]);
}
