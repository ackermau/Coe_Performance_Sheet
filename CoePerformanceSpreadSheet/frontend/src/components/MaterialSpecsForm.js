import { useState, useContext, useEffect } from "react";
import { Button, Typography, Paper, Table, FormControl, InputLabel, MenuItem, Autocomplete, Select, TableBody, TableCell, TableContainer, TableRow, Grid, Divider, TextField } from "@mui/material";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { ArrowDropDown } from "../../node_modules/@mui/icons-material/index";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { RFQFormContext } from "../context/RFQFormContext";

const formatLabel = (label) => {
    return label
        .replace(/([a-z])([A-Z])/g, '$1 $2') // Add space before capital letters following lowercase letters
        .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2') // Ensure groups like "MaxFPM" becomes "Max FPM"
        .trim()
        .replace(/\b(ID|OD|FPM)\b/g, (match) => match.toUpperCase()) // Keep ID, OD, FPM uppercase
        .replace(/\b\w/g, (char) => char.toUpperCase());
};

export default function MaterialSpecsForm() {
    const { materialSpecs, setMaterialSpecs } = useContext(MaterialSpecsContext);
    const { rfqForm } = useContext(RFQFormContext); // <— grab rfqForm context

    const handleChange = (field, value) => {
        setMaterialSpecs((prev) => ({
            ...prev,
            [field]: value
        }));
    };

    useEffect(() => {
        setMaterialSpecs(prev => ({
            ...prev,
            date: rfqForm.rfq_date || prev.date,
            customer: rfqForm.company_name || prev.customer,
            coilWidthWidth: rfqForm.max_coil_width || prev.coilWidthWidth,

            coilWidthMax: rfqForm.max_yield_at_width || prev.coilWidthMax,
            coilWeightMax: rfqForm.max_coil_weight || prev.coilWeightMax,
            materialThicknessMax: rfqForm.max_yield_thickness || prev.materialThicknessMax,
            materialTypeMax: rfqForm.max_yield_material_type || prev.materialTypeMax,
            yieldStrengthMax: rfqForm.max_yield_strength || prev.yieldStrengthMax,
            coilIDMax: rfqForm.coil_inner_diameter || prev.coilIDMax,
            coilODMax: rfqForm.coil_outer_diameter || prev.coilODMax,

            coilWidthFull: rfqForm.max_material_at_width || prev.coilWidthFull,
            coilWeightFull: rfqForm.max_coil_weight || prev.coilWeightFull,
            materialThicknessFull: rfqForm.max_material_thickness || prev.materialThicknessFull,
            materialTypeFull: rfqForm.max_material_material_type || prev.materialTypeFull,
            yieldStrengthFull: rfqForm.max_material_strength || prev.yieldStrengthFull,
            coilIDFull: rfqForm.coil_inner_diameter || prev.coilIDFull,
            coilODFull: rfqForm.coil_outer_diameter || prev.coilODFull,

            coilWidthMin: rfqForm.min_yield_at_width || prev.coilWidthMin,
            coilWeightMin: rfqForm.max_coil_weight || prev.coilWeightMin,
            materialThicknessMin: rfqForm.min_material_thickness || prev.materialThicknessMin,
            materialTypeMin: rfqForm.min_material_material_type || prev.materialTypeMin,
            yieldStrengthMin: rfqForm.min_material_strength || prev.yieldStrengthMin,
            coilIDMin: rfqForm.coil_inner_diameter || prev.coilIDMin,
            coilODMin: rfqForm.coil_outer_diameter || prev.coilODMin,

            coilWidthWidth: rfqForm.max_material_run_at_width || prev.coilWidthWidth,
            coilWeightWidth: rfqForm.max_coil_weight || prev.coilWeightWidth,
            materialThicknessWidth: rfqForm.max_material_run_thickness || prev.materialThicknessWidth,
            materialTypeWidth: rfqForm.max_material_run_material_type || prev.materialTypeWidth,
            yieldStengthWidth: rfqForm.max_material_run_strength || prev.yieldStrengthWidth,
            coilIDWidth: rfqForm.coil_inner_diameter || prev.coilIDWidth,
            coilODWidth: rfqForm.coil_outer_diameter || prev.coilODWidth,
        }));
    }, [rfqForm]);

    // Function to pull data from the RFQ form
    const fetchRFQData = async () => {
        try {
            const response = await fetch("/api/rfq/latest"); // Adjust API route if needed
            if (!response.ok) throw new Error("Failed to fetch RFQ data");

            const rfqData = await response.json();
            setMaterialSpecs((prev) => ({
                ...prev,
                date: rfqData.rfq_date || prev.date,
                customer: rfqData.company_name || prev.customer,
                coilWidthWidth: rfqData.max_coil_width || prev.coilWidthWidth,

                coilWidthMax: rfqData.max_yield_at_width || prev.coilWidthMax,
                coilWeightMax: rfqData.max_coil_weight || prev.coilWeightMax,
                materialThicknessMax: rfqData.max_yield_thickness || prev.materialThicknessMax,
                materialTypeMax: rfqData.max_yield_material_type || prev.materialTypeMax,
                yieldStrengthMax: rfqData.max_yield_tensile_strength || prev.yieldStrengthMax,
                coilIDMax: rfqData.coil_inner_diameter || prev.coilIDMax,
                coilODMax: rfqData.max_coil_outside_diameter || prev.coilODMax,

                coilWidthFull: rfqData.max_material_at_width || prev.coilWidthFull,
                coilWeightFull: rfqData.max_coil_weight || prev.coilWeightFull,
                materialThicknessFull: rfqData.max_material_thickness || prev.materialThicknessFull,
                materialTypeFull: rfqData.max_material_material_type || prev.materialTypeFull,
                yieldStrengthFull: rfqData.max_material_tensile_strength || prev.yieldStrengthFull,
                coilIDFull: rfqData.coil_inner_diameter || prev.coilIDFull,
                coilODFull: rfqData.max_coil_outside_diameter || prev.coilODFull,

                coilWidthMin: rfqData.min_material_at_width || prev.coilWidthMin,
                coilWeightMin: rfqData.max_coil_weight || prev.coilWeightMin,
                materialThicknessMin: rfqData.min_material_thickness || prev.materialThicknessMin,
                materialTypeMin: rfqData.min_material_material_type || prev.materialTypeMin,
                yieldStrengthMin: rfqData.min_material_tensile_strength || prev.yieldStrengthMin,
                coilIDMin: rfqData.coil_inner_diameter || prev.coilIDMin,
                coilODMin: rfqData.max_coil_outside_diameter || prev.coilODMin,

                coilWidthWidth: rfqData.max_material_run_at_width || prev.coilWidthWidth,
                coilWeightWidth: rfqData.max_coil_weight || prev.coilWeightWidth,
                materialThicknessWidth: rfqData.max_material_run_thickness || prev.materialThicknessWidth,
                materialTypeWidth: rfqData.max_material_run_material_type || prev.materialTypeWidth,
                yieldStengthWidth: rfqData.max_material_run_tensile_strength || prev.yieldStrengthWidth,
                coilIDWidth: rfqData.coil_inner_diameter || prev.coilIDWidth,
                coilODWidth: rfqData.max_coil_outside_diameter || prev.coilODWidth,

            }));
        } catch (error) {
            console.error("Error fetching RFQ data:", error);
        }
    };

    const controlsLevelOptions = [
        "Mini-Drive System",
        "Relay Machine",
        "SyncMaster",
        "IP Indexer Basic",
        "Allen Bradley Basic",
        "SyncMaster Plus",
        "IP Indexer Plus",
        "Allen Bradley Plus",
        "Fully Automatic"
    ];

    const typeOfLineOptions = [
        "Compact",
        "Compact CTL",
        "Conventional",
        "Conventional CTL",
        "Pull Through",
        "Pull Through Compact",
        "Pull Through CTL",
        "Feed",
        "Feed-Pull Through",
        "Feed-Pull Through-Shear",
        "Feed-Shear",
        "Straightener",
        "Straightener-Reel Combination",
        "Reel-Motorized",
        "Reel-Pull Off",
        "Threading Table",
        "Other"
    ];

    const passlineOptions = [
        "None",
        "37\"", "39\"", "40\"", "40.5\"", "41\"", "41.5\"", "42\"", "43\"", "43.625\"",
        "44\"", "45\"", "45.5\"", "46\"", "46.5\"", "47\"", "47.4\"", "47.5\"", "48\"", "48.5\"",
        "49\"", "49.5\"", "50\"", "50.5\"", "50.75\"", "51\"", "51.5\"", "51.75\"", "52\"",
        "52.25\"", "52.5\"", "53\"", "54\"", "54.5\"", "54.75\"", "55\"", "55.25\"",
        "55.50\"", "55.75\"", "56\"", "56.50\"", "57\"", "58\"", "58.25\"", "59\"",
        "59.50\"", "60\"", "60.50\"", "61\"", "62\"", "62.5\"", "63\"", "64\"", "64.5\"",
        "65\"", "66\"", "66.5\"", "67\"", "70\"", "72\"", "75\"", "76\""
    ];

    const rollOptions = [
        "7 Roll Str. Backbend", "9 Roll Str. Backbend", "11 Roll Str. Backbend"
    ];

    const reelBackplateOptions = [
        "Standard Backplate", "Full OD Backplate"
    ];

    const reelStyleOptions = [
        "Single Ended", "Double Ended"
    ];

    return (
        <Paper className="p-6 max-w-4xl mx-auto shadow-md">
            <Typography variant="h4" gutterBottom align="center">Material Specifications</Typography>

            {/* Smaller Tables for Each Section */}
            <Grid item xs={12}><Divider /><Typography variant="h5">Customer Information</Typography></Grid>
            <Grid item xs={12} sm={4}>
                <TextField size="small"
                           label="Customer"
                           value={materialSpecs.customer}
                           onChange={(e) => handleChange("customer", e.target.value)}
                           fullWidth />
            </Grid>
            {["date", "reference"].map((field) => (
                <Grid item xs={12} sm={4} key={field}>
                    <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                </Grid>
            ))}

            <Grid TableContainer display="flex" flexDirection="row">
                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Max Thickness</Typography></Grid>
                    <Grid item xs={12} sm={4} key={"materialTypeMax"}>
                        <TextField size="small" label={formatLabel("materialTypeMax")} value={materialSpecs["materialTypeMax"]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                    {["coilWidthMax", "coilWeightMax", "materialThicknessMax", 
                      "yieldStrengthMax", "materialTensileMax", "requiredMaxFPMMax", "minBendRadiusMax",
                      "minLoopLengthMax", "coilODMax", "coilIDMax", "coilODCalculatedMax"].map((field) => (
                        <Grid item xs={12} sm={4} key={field}>
                            <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                        </Grid>
                      ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Max @ Full</Typography></Grid>
                    <Grid item xs={12} sm={4} key={"materialTypeFull"}>
                        <TextField size="small" label={formatLabel("materialTypeFull")} value={materialSpecs["materialTypeFull"]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                    {["coilWidthFull", "coilWeightFull", "materialThicknessFull",
                        "yieldStrengthFull", "materialTensileFull", "requiredMaxFPMFull", "minBendRadiusFull",
                        "minLoopLengthFull", "coilODFull", "coilIDFull", "coilODCalculatedFull"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Min Thickness</Typography></Grid>
                    <Grid item xs={12} sm={4} key={"materialTypeMin"}>
                        <TextField size="small" label={formatLabel("materialTypeMin")} value={materialSpecs["materialTypeMin"]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                    {["coilWidthMin", "coilWeightMin", "materialThicknessMin",
                        "yieldStrengthMin", "materialTensileMin", "requiredMaxFPMMin", "minBendRadiusMin",
                        "minLoopLengthMin", "coilODMin", "coilIDMin", "coilODCalculatedMin"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Max @ Width</Typography></Grid>
                    <Grid item xs={12} sm={4} key={"materialTypeWidth"}>
                        <TextField size="small" label={formatLabel("materialTypeWidth")} value={materialSpecs["materialTypeWidth"]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                    {["coilWidthWidth", "coilWeightWidth", "materialThicknessWidth", 
                        "yieldStrengthWidth", "materialTensileWidth", "requiredMaxFPMWidth", "minBendRadiusWidth",
                        "minLoopLengthWidth", "coilODWidth", "coilIDWidth", "coilODCalculatedWidth"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>
            </Grid>

            <Grid item xs={12}><Divider /><Typography variant="h5">Feed System</Typography></Grid>
            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Feed Direction</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.feedDirection}
                            onChange={(e) => handleChange("feedDirection", e.target.value)}
                            IconComponent={ArrowDropDown}>
                        <MenuItem value="LtoR">Left to Right</MenuItem>
                        <MenuItem value="RtoL">Right to Left</MenuItem>
                        </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Controls Level</Typography>
                <FormControl fullWidth size="small">
                    <Select
                        value={materialSpecs.controlsLevel || ""}
                        onChange={(e) => handleChange("controlsLevel", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        {controlsLevelOptions.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Type of Line</Typography>
                <FormControl fullWidth size="small">
                    <Select
                        value={materialSpecs.typeOfLine || ""}
                        onChange={(e) => handleChange("typeOfLine", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        {typeOfLineOptions.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={4} key={"feedControls"}>
                <TextField size="small" label={formatLabel("feedControls")} value={materialSpecs["feedControls"]} onChange={(e) => handleChange("feedControls", e.target.value)} fullWidth />
            </Grid>

            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 100 }}>Passline</Typography>
                <Autocomplete
                    options={passlineOptions}
                    value={materialSpecs.passline || ""}
                    onChange={(e, newValue) => handleChange("passline", newValue)}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            size="small"
                            fullWidth
                            InputProps={{
                                ...params.InputProps,
                                inputProps: {
                                    ...params.inputProps,
                                    style: {
                                        minWidth: 0,
                                        width: '50%'
                                    }
                                }
                            }}
                        />
                    )}
                    disableClearable
                />
            </Grid>

            <Grid item xs={12}><Divider /><Typography variant="h5">Roll Selection</Typography></Grid>
            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Select Roll</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.selectRoll || ""}
                        onChange={(e) => handleChange("selectRoll", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        {rollOptions.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12}><Divider /><Typography variant="h5">Reel Information</Typography></Grid>
            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Reel Backplate</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.reelBackplate || ""}
                        onChange={(e) => handleChange("reelBackplate", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        {reelBackplateOptions.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>    
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Reel Style</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.reelStyle || ""}
                        onChange={(e) => handleChange("reelStyle", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        {reelStyleOptions.map((option) => (
                            <MenuItem key={option} value={option}>{option}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12}><Divider /><Typography variant="h5">Non-Marking</Typography></Grid>
            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Light Guage Non-Marking</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.lightGuageNonMarking || ""}
                        onChange={(e) => handleChange("lightGuageNonMarking", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        <MenuItem value="Yes">Yes</MenuItem>
                        <MenuItem value="No">No</MenuItem>
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Non-Marking</Typography>
                <FormControl fullWidth size="small">
                    <Select value={materialSpecs.nonMarking || ""}
                        onChange={(e) => handleChange("nonMarking", e.target.value)}
                        IconComponent={ArrowDropDown}>
                        <MenuItem value="Yes">Yes</MenuItem>
                        <MenuItem value="No">No</MenuItem>
                    </Select>
                </FormControl>
            </Grid>

            {/* Pull Data Button */}
            <Button variant="contained" color="primary" className="mt-4" fullWidth onClick={fetchRFQData}>
                Pull Data from RFQ
            </Button>
        </Paper>
    );
}
