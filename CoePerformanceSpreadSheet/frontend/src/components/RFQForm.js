import { useState } from "react";
import { Button, TextField, Grid, Typography, Paper, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, Divider } from "@mui/material";
import { ArrowDropDown } from "../../node_modules/@mui/icons-material/index";

const formatLabel = (label) => {
    return label
        .replace(/_/g, " ") // Replace underscores with spaces
        .replace(/\b\w/g, (char) => char.toUpperCase()); // Capitalize the first letter of each word
};

export default function RFQPage() {
    const [rfq, setRFQ] = useState({
        rfq_date: "",
        company_name: "",
        state_province: "",
        street_address: "",
        zip_code: "",
        city: "",
        country: "",
        contact_name: "",
        contact_position: "",
        contact_phone: "",
        contact_email: "",
        dealer_name: "",
        dealer_salesman: "",

        number_days_running: "",
        number_of_shifts: "",
        line_application: "",
        line_type: "",
        pull_through: false,
        max_coil_width: "",
        min_coil_width: "",
        coil_inner_diameter: "",
        max_coil_weight: "",
        max_coil_outside_diameter: "",
        max_coil_handling_capacity: "",
        slit_edge: false,
        mill_edge: false,
        coil_car_required: false,
        running_off_backplate: false,
        require_rewinding: false,

        max_yield_thickness: "",
        max_yield_material_type: "",
        max_yield_strength: "",
        max_yield_at_width: "",
        max_yield_tensile_strength: "",
        max_material_thickness: "",
        max_material_material_type: "",
        max_material_strength: "",
        max_material_at_width: "",
        max_material_tensile_strength: "",
        min_material_thickness: "",
        min_material_material_type: "",
        min_material_strength: "",
        min_material_at_width: "",
        min_material_tensile_strength: "",
        max_material_run_thickness: "",
        max_material_run_material_type: "",
        max_material_run_strength: "",
        max_material_run_at_width: "",
        max_material_run_tensile_strength: "",
        cosmetic: false,
        current_brand_feed_equipment: "",

        gap_frame_press: false,
        obi: false,
        shear_die_application: false,
        hydraulic_press: false,
        servo_press: false,
        straight_side_press: false,
        other: false,
        tonnage_of_press: "",
        press_bed_area_width: "",
        press_bed_area_length: "",
        press_stroke_length: "",
        window_opening_size: "",
        press_max_spm: "",
        transfer_dies: false,
        progressive_dies: false,
        blanking_dies: false,

        average_feed_length: "",
        average_spm: "",
        max_feed_length: "",
        average_spm: "",
        min_feed_length: "",
        average_spm: "",
        feed_window_degrees: "",
        press_cycle_time: "",
        voltage_required: "",
    });

    const handleChange = (field, value) => {
        setRFQ({ ...rfq, [field]: value });
    };

    const createRFQ = async () => {
        const response = await fetch("/api/rfq/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(rfq),
        });
        const data = await response.json();
        console.log("RFQ Created:", data);
    };

    const lineTypeOptions = {
        "Press Feed": ["Conventional", "Compact"],
        "Cut to Length": ["Conventional", "Compact"],
        "Standalone": ["Feed", "Straightener", "Reel-Motorized", "Reel-Pull Off", "Straightener-Reel Combination", "Feed Shear", "Threading Table", "Other"]
    };

    return (
        <Paper className="p-6 max-w-6xl mx-auto shadow-md">
            <Typography variant="h3" align="center" gutterBottom>Request for Quote (RFQ)</Typography>

            <Grid container spacing={1}>
                {/* Company Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Company Information</Typography></Grid>
                {["company_name", "state_province", "street_address", "zip_code", "city", "country"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                {/* Contact Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Contact Information</Typography></Grid>
                {["contact_name", "contact_position", "contact_phone", "contact_email"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                {/* Dealer Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Dealer Information</Typography></Grid>
                {["dealer_name", "dealer_salesman"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                {/* Running Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Running Specifications</Typography></Grid>
                {["number_days_running", "number_of_shifts"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                {/* Line Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Line Specifications</Typography></Grid>
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>{formatLabel("line_application")}</InputLabel>
                        <Select
                                value={rfq.line_application}
                                onChange={(e) => handleChange("line_application", e.target.value)}
                                IconComponent={ArrowDropDown}>
                            <MenuItem value=""><em>None</em></MenuItem>
                            <MenuItem value="Press Feed">Press Feed</MenuItem>
                            <MenuItem value="Cut to Length">Cut to Length</MenuItem>
                            <MenuItem value="Standalone">Standalone</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>{formatLabel("line_type")}</InputLabel>
                        <Select 
                                value={rfq.line_type}
                                onChange={(e) => handleChange("line_type", e.target.value)}
                                IconComponent={ArrowDropDown}>
                            <MenuItem value=""><em>None</em></MenuItem>
                            {lineTypeOptions[rfq.line_application]?.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfq.pull_through} onChange={(e) => handleChange("pull_through", e.target.checked)} />} label={formatLabel("pull_through")} />
                </Grid>

                {/* Coil Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Coil Specifications</Typography></Grid>
                {["max_coil_width", "min_coil_width", "coil_inner_diameter", "max_coil_weight", "max_coil_outside_diameter", "max_coil_handling_capacity"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                {["slit_edge", "mill_edge", "coil_car_required", "running_off_backplate", "require_rewinding"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfq[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                {/* Material Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Highest Yield</Typography></Grid>
                {["max_yield_thickness",  "max_yield_strength", "max_yield_at_width", "max_yield_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={3} key="max_yield_type">
                    <TextField size="small" label={"Material Type"} value={rfq.max_material_mat_type} onChange={(e) => handleChange("max_yield_type", e.target.value)} fullWidth />
                </Grid>
                <Grid item xs={12}><Divider /><Typography variant="h5">Max Material Thickness</Typography></Grid>
                {["max_material_thickness", "max_material_strength", "max_material_at_width", "max_material_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={3} key="max_material_mat_type">
                    <TextField size="small" label={"Material Type"} value={rfq.max_material_mat_type} onChange={(e) => handleChange("max_material_mat_type", e.target.value)} fullWidth />
                </Grid>
                <Grid item xs={12}><Divider /><Typography variant="h5">Min Material Thickness</Typography></Grid>
                {["min_material_thickness",  "min_material_strength", "min_material_at_width", "min_material_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={3} key="min_material_mat_type">
                    <TextField size="small" label={"Material Type"} value={rfq.max_material_mat_type} onChange={(e) => handleChange("min_material_mat_type", e.target.value)} fullWidth />
                </Grid>
                <Grid item xs={12}><Divider /><Typography variant="h5">Max Material Thickness to be Run</Typography></Grid>
                {["max_material_run_thickness", "max_material_run_strength", "max_material_run_at_width", "max_materialrun__tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={3} key="max_material_mat_run_type">
                    <TextField size="small" label={"Material Type"} value={rfq.max_material_mat_type} onChange={(e) => handleChange("max_material_mat_run_type", e.target.value)} fullWidth />
                </Grid>

                <Grid item xs={12}><Divider /></Grid>
                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfq.cosmetic} onChange={(e) => handleChange("cosmetic", e.target.checked)} />} label={formatLabel("cosmetic")} />
                </Grid>

                <Grid item xs={12}><Divider /></Grid>
                <Grid item xs={12} sm={6}>
                    <TextField size="small" label={formatLabel("current_brand_feed_equipment")} value={rfq.current_brand_feed_equipment} onChange={(e) => handleChange("current_brand_feed_equipment", e.target.value)} fullWidth />
                </Grid>
            </Grid>

            <Grid container spacing={1}>
                {/* Press Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Type of Press</Typography></Grid>
                {["gap_frame_press", "obi", "shear_dia_application", "hydraulic_press", "servo_press", "straight_side_press", "other"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfq[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}

                <Grid item xs={12}><Divider /></Grid>
                {["tonnage_of_press", "press_bed_area_width", "press_bed_area_length", "press_stroke_length", "window_opening_size", "press_max_spm"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                <Grid item xs={12}><Divider /><Typography variant="h5">Type of Dies</Typography></Grid>
                {["transfer_dies", "progressive_dies", "blanking_dies"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfq[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {["average_feed_length", "max_feed_length", "min_feed_length"].map((field) => (
                            <Grid item key={field}>
                                <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {["average_spm", "max_spm", "min_spm"].map((field) => (
                            <Grid item key={field}>
                                <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {["feed_window_degrees", "press_cycle_time"].map((field) => (
                            <Grid item key={field}>
                                <TextField size="small" label={formatLabel(field)} value={rfq[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>

                <Grid item xs={12} sm={4}>
                    <TextField size="small" label={formatLabel("voltage_required")} value={rfq.voltage_required} onChange={(e) => handleChange("voltage_required", e.target.value)} fullWidth />
                </Grid>
            </Grid>

            <Grid container spacing={1}>
                
            </Grid>

            <Grid item xs={12} className="text-center mt-4">
                <Button onClick={createRFQ} variant="contained" color="primary" size="large">Submit RFQ</Button>
            </Grid>
        </Paper>
    );
}