import { useState } from "react";
import { useContext } from "react";
import { Button, TextField, Grid, Typography, Paper, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, Divider } from "@mui/material";
import { ArrowDropDown } from "../../node_modules/@mui/icons-material/index";
import { RFQFormContext } from "../context/RFQFormContext";
import { API_URL } from '../config';

const formatLabel = (label) => {
    return label
        .replace(/_/g, " ") // Replace underscores with spaces
        .replace(/\b\w/g, (char) => char.toUpperCase()); // Capitalize the first letter of each word
};

export default function RFQForm() {
    const { rfqForm, setRFQForm } = useContext(RFQFormContext);

    const handleChange = (field, value) => {
        setRFQForm((prev) => {
            const updated = { ...prev, [field]: value };

            // FPM mapping
            const fpmMap = {
                average_feed_length: ["average_feed_length", "average_spm", "average_fpm"],
                average_spm: ["average_feed_length", "average_spm", "average_fpm"],
                max_feed_length: ["max_feed_length", "max_spm", "max_fpm"],
                max_spm: ["max_feed_length", "max_spm", "max_fpm"],
                min_feed_length: ["min_feed_length", "min_spm", "min_fpm"],
                min_spm: ["min_feed_length", "min_spm", "min_fpm"]
            };

            const fpmParams = fpmMap[field];
            if (fpmParams) {
                const [lenField, spmField, resultField] = fpmParams;
                const feedLength = field === lenField ? parseFloat(value) : parseFloat(prev[lenField]);
                const spm = field === spmField ? parseFloat(value) : parseFloat(prev[spmField]);

                if (!isNaN(feedLength) && !isNaN(spm)) {
                    fetchFPM(feedLength, spm, resultField);
                } else {
                    // If either input is invalid, clear the FPM
                    setTimeout(() => {
                        setRFQForm((prev) => ({
                            ...prev,
                            [resultField]: ""
                        }));
                    }, 0);
                }
            }

            return updated;
        });
    };

    const fetchFPM = async (feedLength, spm, resultField) => {
        try {
            const response = await fetch(`${API_URL}/api/rfq/calculate_fpm`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ feed_length: feedLength, spm: spm }),
            });

            const data = await response.json();
            console.log("Fetched FPM for", resultField, "=", data.fpm);

            setRFQForm((prev) => ({
                ...prev,
                [resultField]: data.fpm
            }));
        } catch (err) {
            console.error("Error fetching FPM:", err);
        }
    };

    const [rfqFormContext, setRFQFormContext] = useState({
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
        alloted_length: "",
        alloted_width: "",
        feed_mounted_press: false,
        adequate_support: false,
        average_fpm: "",
        max_fpm: "",
        min_fpm: "",

        custom_mounting_plates: false,
        passline_height: "",
        loop_pit: false,
        coil_change_time_concern: false,
        coil_change_time_goal: "",
        feed_direction: "",
        coil_loading: "",
        guarding_safety: "",

        decision_date: "",
        ideal_delivery_date: "",
        earliest_date_excpect_delivery: "",
        latest_date_excpect_delivery: "",
        special_consideration: "",
    });

    const createRFQ = async () => {
        const response = await fetch("/api/rfq/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(rfqForm),
        });
        rfqForm.rfq_date = new Date().toISOString().split('T')[0]; // Add the current date
        const data = await response.json();
        console.log("RFQ Created:", data);
    };

    const lineTypeOptions = {
        "Press Feed": ["Conventional", "Compact"],
        "Cut to Length": ["Conventional", "Compact"],
        "Standalone": ["Feed", "Straightener", "Reel-Motorized", "Reel-Pull Off", "Straightener-Reel Combination", "Feed Shear", "Threading Table", "Other"]
    };

    const materialTypeOptions = {
        "max_yield_material_type": ["Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass",  "Beryl Copper"],
        "max_material_material_type": ["Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"],
        "min_material_material_type": ["Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"],
        "max_material_run_material_type": ["Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"]
    };

    return (
        <Paper className="p-6 max-w-6xl mx-auto shadow-md">
            <Typography variant="h3" align="center" gutterBottom>Request for Quote (RFQ)</Typography>

            <Grid container spacing={1}>
                {/* Company Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Company Information</Typography></Grid>
                {["company_name", "state_province", "street_address", "zip_code", "city", "country"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                {/* Contact Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Contact Information</Typography></Grid>
                {["contact_name", "contact_position", "contact_phone", "contact_email"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                {/* Dealer Details */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Dealer Information</Typography></Grid>
                {["dealer_name", "dealer_salesman"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                {/* Running Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Running Specifications</Typography></Grid>
                <Grid item xs={12} sm={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Number of days running</Typography>
                    <FormControl>
                        <Select value={rfqForm.number_days_running}
                                onChange={(e) => handleChange("number_days_running", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            <MenuItem value="1">1</MenuItem>
                            <MenuItem value="2">2</MenuItem>
                            <MenuItem value="3">3</MenuItem>
                            <MenuItem value="4">4</MenuItem>
                            <MenuItem value="5">5</MenuItem>
                            <MenuItem value="6">6</MenuItem>
                            <MenuItem value="7">7</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Number of shifts</Typography>
                    <FormControl>
                        <Select value={rfqForm.number_of_shifts}
                            onChange={(e) => handleChange("number_of_shifts", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            <MenuItem value="1">1</MenuItem>
                            <MenuItem value="2">2</MenuItem>
                            <MenuItem value="3">3</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>

                {/* Line Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Line Specifications</Typography></Grid>
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>{formatLabel("line_application")}</InputLabel>
                        <Select 
                                value={rfqForm.line_application}
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
                            value={rfqForm.line_type}
                            onChange={(e) => handleChange("line_type", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            <MenuItem value=""><em>None</em></MenuItem>
                            {lineTypeOptions[rfqForm.line_application]?.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>
                        ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.pull_through} onChange={(e) => handleChange("pull_through", e.target.checked)} />} label={formatLabel("pull_through")} />
                </Grid>

                {/* Coil Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Coil Specifications</Typography></Grid>
                {["max_coil_width", "min_coil_width", "coil_inner_diameter", "max_coil_weight", "max_coil_outside_diameter", "max_coil_handling_capacity"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                {["slit_edge", "mill_edge", "coil_car_required", "running_off_backplate", "require_rewinding"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfqForm[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                {/* Material Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Highest Yield</Typography></Grid>
                {["max_yield_thickness",  "max_yield_strength", "max_yield_at_width", "max_yield_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={6} key="max_yield_material_type">
                    <FormControl fullWidth>
                        <InputLabel>Material Type</InputLabel>
                        <Select
                            value={rfqForm.max_yield_material_type}
                            onChange={(e) => handleChange("max_yield_material_type", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            {materialTypeOptions["max_yield_material_type"]?.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12}><Divider /><Typography variant="h5">Max Material Thickness</Typography></Grid>
                {["max_material_thickness", "max_material_strength", "max_material_at_width", "max_material_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={6} key="max_material_material_type">
                    <FormControl fullWidth>
                        <InputLabel>Material Type</InputLabel>
                        <Select
                            value={rfqForm.max_material_material_type}
                            onChange={(e) => handleChange("max_material_material_type", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            {materialTypeOptions["max_material_material_type"]?.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12}><Divider /><Typography variant="h5">Min Material Thickness</Typography></Grid>
                {["min_material_thickness",  "min_material_strength", "min_material_at_width", "min_material_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={6} key="min_material_material_type">
                    <FormControl fullWidth>
                        <InputLabel>Material Type</InputLabel>
                        <Select
                            value={rfqForm.min_material_material_type}
                            onChange={(e) => handleChange("min_material_material_type", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            {materialTypeOptions["min_material_material_type"]?.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12}><Divider /><Typography variant="h5">Max Material Thickness to be Run</Typography></Grid>
                {["max_material_run_thickness", "max_material_run_strength", "max_material_run_at_width", "max_material_run_tensile_strength"].map((field) => (
                    <Grid item xs={12} sm={5} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
                <Grid item xs={12} sm={6} key="max_material_run_material_type">
                    <FormControl fullWidth>
                        <InputLabel>Material Type</InputLabel>
                        <Select
                            value={rfqForm.max_material_run_material_type}
                            onChange={(e) => handleChange("max_material_run_material_type", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            {materialTypeOptions["max_material_run_material_type"]?.map((option) => (
                                <MenuItem key={option} value={option}>{option}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12}><Divider /></Grid>
                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.cosmetic} onChange={(e) => handleChange("cosmetic", e.target.checked)} />} label={formatLabel("cosmetic")} />
                </Grid>

                <Grid item xs={12}><Divider /></Grid>
                <Grid item xs={12} sm={6}>
                    <TextField size="small" label={formatLabel("current_brand_feed_equipment")} value={rfqForm.current_brand_feed_equipment} onChange={(e) => handleChange("current_brand_feed_equipment", e.target.value)} fullWidth />
                </Grid>
            </Grid>

            <Grid container spacing={1}>
                {/* Press Specifications */}
                <Grid item xs={12}><Divider /><Typography variant="h5">Type of Press</Typography></Grid>
                {["gap_frame_press", "obi", "shear_dia_application", "hydraulic_press", "servo_press", "straight_side_press", "other"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfqForm[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}

                <Grid item xs={12}><Divider /></Grid>
                {["tonnage_of_press", "press_bed_area_width", "press_bed_area_length", "press_stroke_length", "window_opening_size", "press_max_spm"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}

                <Grid item xs={12}><Divider /><Typography variant="h5">Type of Dies</Typography></Grid>
                {["transfer_dies", "progressive_dies", "blanking_dies"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <FormControlLabel control={<Checkbox checked={rfqForm[field]} onChange={(e) => handleChange(field, e.target.checked)} />} label={formatLabel(field)} />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                {/* Feed and Coil Specifications */}
                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {["average_feed_length", "max_feed_length", "min_feed_length"].map((field) => (
                            <Grid item key={field}>
                                <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {[
                            { length: "average_feed_length", spm: "average_spm", fpm: "average_fpm", label: "Average" },
                            { length: "max_feed_length", spm: "max_spm", fpm: "max_fpm", label: "Max" },
                            { length: "min_feed_length", spm: "min_spm", fpm: "min_fpm", label: "Min" }
                        ].map(({ length, spm, fpm, label }) => (
                            <Grid item key={spm}>
                                <TextField
                                    size="small"
                                    label={formatLabel(spm)}
                                    value={rfqForm[spm] ?? ""}
                                    onChange={(e) => handleChange(spm, e.target.value)}
                                    fullWidth
                                />
                                <Typography variant="body2" color="textSecondary">
                                    {label} FPM: {rfqForm[fpm] || ""}
                                </Typography>
                            </Grid>
                        ))}
                    </Grid>
                </Grid>

                <Grid item xs={12} sm={4}>
                    <Grid container direction="column" spacing={1}>
                        {["feed_window_degrees", "press_cycle_time"].map((field) => (
                            <Grid item key={field}>
                                <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                    </Grid>
                </Grid>

                <Grid item xs={12} sm={4}>
                    <TextField size="small" label={formatLabel("voltage_required")} value={rfqForm.voltage_required ?? ""} onChange={(e) => handleChange("voltage_required", e.target.value)} fullWidth />
                </Grid>

                <Grid item xs={12}><Divider /></Grid>
                {["alloted_length", "alloted_width"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth key={field} />
                        <Typography variant="h5">(ft)</Typography>
                    </Grid>
                ))}

                <Grid item xs={12} sm={7}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.feed_mounted_press} onChange={(e) => handleChange("feed_mounted_press", e.target.checked)} />} label={"Can feeder be mounted to press?"} />
                </Grid>

                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.adequate_support} onChange={(e) => handleChange("adequate_support", e.target.checked)} />} label={"If yes, we must verify there is adequate support to mount to. Is there adequate support?"} />
                </Grid>

                <Grid item xs={12} sm={6}>
                    <Typography >If no, it will need a cabinet.</Typography>
                </Grid>
            </Grid>

            <Grid container spacing={1}>
                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.custom_mounting_plates} onChange={(e) => handleChange("custom_mounting_plates", e.target.checked)} />} label={"Will you need custom mounting plate(s)?"} />
                </Grid>

                {["passline_height"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth key={field} />
                        <Typography variant="h5">(ft)</Typography>
                    </Grid>
                ))}

                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.loop_pit} onChange={(e) => handleChange("loop_pit", e.target.checked)} />} label={"Will there be a loop pit?"} />
                </Grid>

                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.coil_change_time_concern} onChange={(e) => handleChange("coil_change_time_concern", e.target.checked)} />} label={"Is coil change time a concern?"} />
                </Grid>

                {["coil_change_time_goal"].map((field) => (
                    <Grid item xs={12} sm={7} key={field}>
                        <Typography >If so, what is your coil change time goal? (min)</Typography>
                        <TextField size="small" onChange={(e) => handleChange(field, e.target.value)} fullWidth key={field} />
                    </Grid>
                ))}

                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>{formatLabel("feed_direction")}</InputLabel>
                        <Select
                            value={rfqForm.feed_direction}
                            onChange={(e) => handleChange("feed_direction", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            <MenuItem value="left_to_right">Left to Right</MenuItem>
                            <MenuItem value="right_to_left">Right to Left</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                        <InputLabel>{formatLabel("coil_loading")}</InputLabel>
                        <Select
                            value={rfqForm.coil_loading}
                            onChange={(e) => handleChange("coil_loading", e.target.value)}
                            IconComponent={ArrowDropDown}>
                            <MenuItem value="operator_side">Operator Side</MenuItem>
                            <MenuItem value="non_operator_side">Non-Operator Side</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} sm={6}>
                    <FormControlLabel control={<Checkbox checked={rfqForm.guarding_safety} onChange={(e) => handleChange("guarding_safety", e.target.checked)} />} label={"Will your line require guarding or special safety requirements?"} />
                </Grid>
            </Grid>

            <Grid container spacing={1}>
                {["decision_date", "ideal_delivery_date", "earliest_date_excpect_delivery", "latest_date_excpect_delivery"].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="date" value={rfqForm[field] ?? ""} onChange={(e) => handleChange(field, e.target.value)} fullWidth InputLabelProps={{ shrink: true }} />
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={1}>
                <TextField size="small" onChange={(e) => handleChange(rfqForm.special_consideration, e.target.value)} fullWidth />
            </Grid>

            <Grid item xs={12} className="text-center mt-4">
                <Button onClick={createRFQ} variant="contained" color="primary" size="large">Submit RFQ</Button>
            </Grid>
        </Paper>
    );
}