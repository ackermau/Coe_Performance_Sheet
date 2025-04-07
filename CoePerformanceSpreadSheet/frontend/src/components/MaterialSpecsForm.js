import { useContext, useEffect } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, Tabs, Tab, FormControl, Select, MenuItem, Autocomplete, Button
} from "@mui/material";
import { ArrowDropDown } from "../../node_modules/@mui/icons-material/index";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { RFQFormContext } from "../context/RFQFormContext";
import { useSharedMaterialView } from "../hooks/useSharedMaterialView";
import { API_URL } from '../config';

const formatLabel = (label) => {
    return label
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
        .trim()
        .replace(/\b(ID|OD|FPM)\b/g, (match) => match.toUpperCase())
        .replace(/\b\w/g, (char) => char.toUpperCase());
};

export default function MaterialSpecsForm() {
    const { materialSpecs, setMaterialSpecs } = useContext(MaterialSpecsContext);
    const { rfqForm } = useContext(RFQFormContext);
    const { activeView, setActiveView, viewConfigs } = useSharedMaterialView();

    // Update state and trigger backend calculation when any field changes.
    const handleChange = (field, value) => {
        const updated = { ...materialSpecs, [field]: value };
        setMaterialSpecs(updated);
        triggerBackendCalculation(updated);
    };

    // Call the backend API to recalculate values when inputs change.
    const triggerBackendCalculation = async (payload) => {
        try {
            const response = await fetch(`${API_URL}/api/material_specs/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            // Merge the computed values from the backend into the current specs.
            setMaterialSpecs((prev) => ({ ...prev, ...data }));
        } catch (err) {
            console.error("Backend calculation failed: ", err);
        }
    };

    // Set default values from rfqForm when it changes.
    useEffect(() => {
        const updatedSpecs = {
            ...materialSpecs,
            date: rfqForm.rfq_date || materialSpecs.date,
            customer: rfqForm.company_name || materialSpecs.customer,
            coilWidthWidth: rfqForm.max_coil_width || materialSpecs.coilWidthWidth,

            coilWidthMax: rfqForm.max_yield_at_width || materialSpecs.coilWidthMax,
            coilWeightMax: rfqForm.max_coil_weight || materialSpecs.coilWeightMax,
            materialThicknessMax: rfqForm.max_yield_thickness || materialSpecs.materialThicknessMax,
            materialTypeMax: rfqForm.max_yield_material_type || materialSpecs.materialTypeMax,
            yieldStrengthMax: rfqForm.max_yield_strength || materialSpecs.yieldStrengthMax,
            coilIDMax: rfqForm.coil_inner_diameter || materialSpecs.coilIDMax,
            coilODMax: rfqForm.max_coil_outside_diameter || materialSpecs.coilODMax,
            requiredMaxFPMMax: rfqForm.max_fpm || materialSpecs.requiredMaxFPMMax,

            coilWidthFull: rfqForm.max_material_at_width || materialSpecs.coilWidthFull,
            coilWeightFull: rfqForm.max_coil_weight || materialSpecs.coilWeightFull,
            materialThicknessFull: rfqForm.max_material_thickness || materialSpecs.materialThicknessFull,
            materialTypeFull: rfqForm.max_material_material_type || materialSpecs.materialTypeFull,
            yieldStrengthFull: rfqForm.max_material_strength || materialSpecs.yieldStrengthFull,
            coilIDFull: rfqForm.coil_inner_diameter || materialSpecs.coilIDFull,
            coilODFull: rfqForm.max_coil_outside_diameter || materialSpecs.coilODFull,
            requiredMaxFPMFull: rfqForm.max_fpm || materialSpecs.requiredMaxFPMFull,

            coilWidthMin: rfqForm.min_material_at_width || materialSpecs.coilWidthMin,
            coilWeightMin: rfqForm.max_coil_weight || materialSpecs.coilWeightMin,
            materialThicknessMin: rfqForm.min_material_thickness || materialSpecs.materialThicknessMin,
            materialTypeMin: rfqForm.min_material_material_type || materialSpecs.materialTypeMin,
            yieldStrengthMin: rfqForm.min_material_strength || materialSpecs.yieldStrengthMin,
            coilIDMin: rfqForm.coil_inner_diameter || materialSpecs.coilIDMin,
            coilODMin: rfqForm.max_coil_outside_diameter || materialSpecs.coilODMin,
            requiredMaxFPMMin: rfqForm.max_fpm || materialSpecs.requiredMaxFPMMin,

            coilWidthWidth: rfqForm.max_material_run_at_width || materialSpecs.coilWidthWidth,
            coilWeightWidth: rfqForm.max_coil_weight || materialSpecs.coilWeightWidth,
            materialThicknessWidth: rfqForm.max_material_run_thickness || materialSpecs.materialThicknessWidth,
            materialTypeWidth: rfqForm.max_material_run_material_type || materialSpecs.materialTypeWidth,
            yieldStrengthWidth: rfqForm.max_material_run_strength || materialSpecs.yieldStrengthWidth,
            coilIDWidth: rfqForm.coil_inner_diameter || materialSpecs.coilIDWidth,
            coilODWidth: rfqForm.max_coil_outside_diameter || materialSpecs.coilODWidth,
            requiredMaxFPMWidth: rfqForm.max_fpm || materialSpecs.requiredMaxFPMWidth,
        };

        setMaterialSpecs(updatedSpecs);
        triggerBackendCalculation(updatedSpecs);
    }, [rfqForm]);

    const extraFieldsByView = {
        max: [
            "coilWeightMax", "materialTensileMax", "requiredMaxFPMMax",
            "minBendRadiusMax", "minLoopLengthMax", "coilODMax", "coilIDMax", "coilODCalculatedMax"
        ],
        full: [
            "coilWeightFull", "materialTensileFull", "requiredMaxFPMFull",
            "minBendRadiusFull", "minLoopLengthFull", "coilODFull", "coilIDFull", "coilODCalculatedFull"
        ],
        min: [
            "coilWeightMin", "materialTensileMin", "requiredMaxFPMMin",
            "minBendRadiusMin", "minLoopLengthMin", "coilODMin", "coilIDMin", "coilODCalculatedMin"
        ],
        width: [
            "coilWeightWidth", "materialTensileWidth", "requiredMaxFPMWidth",
            "minBendRadiusWidth", "minLoopLengthWidth", "coilODWidth", "coilIDWidth", "coilODCalculatedWidth"
        ]
    };

    const passlineOptions = [
        "None", "37\"", "39\"", "40\"", "40.5\"", "41\"", "41.5\"", "42\"", "43\"", "43.625\"", "44\"", "45\"", "45.5\"", "46\"", "46.5\"",
        "47\"", "47.4\"", "47.5\"", "48\"", "48.5\"", "49\"", "49.5\"", "50\"", "50.5\"", "50.75\"", "51\"", "51.5\"", "51.75\"", "52\"",
        "52.25\"", "52.5\"", "53\"", "54\"", "54.5\"", "54.75\"", "55\"", "55.25\"", "55.50\"", "55.75\"", "56\"", "56.50\"", "57\"", "58\"",
        "58.25\"", "59\"", "59.50\"", "60\"", "60.50\"", "61\"", "62\"", "62.5\"", "63\"", "64\"", "64.5\"", "65\"", "66\"", "66.5\"", "67\"",
        "70\"", "72\"", "75\"", "76\""
    ];

    const controlsLevelOptions = [
        "Mini-Drive System", "Relay Machine", "SyncMaster", "IP Indexer Basic", "Allen Bradley Basic",
        "SyncMaster Plus", "IP Indexer Plus", "Allen Bradley Plus", "Fully Automatic"
    ];

    const typeOfLineOptions = [
        "Compact", "Compact CTL", "Conventional", "Conventional CTL", "Pull Through", "Pull Through Compact",
        "Pull Through CTL", "Feed", "Feed-Pull Through", "Feed-Pull Through-Shear", "Feed-Shear",
        "Straightener", "Straightener-Reel Combination", "Reel-Motorized", "Reel-Pull Off",
        "Threading Table", "Other"
    ];

    const rollOptions = ["7 Roll Str. Backbend", "9 Roll Str. Backbend", "11 Roll Str. Backbend"];
    const reelBackplateOptions = ["Standard Backplate", "Full OD Backplate"];
    const reelStyleOptions = ["Single Ended", "Double Ended"];

    const materialTypeFields = [
        "materialTypeMax", "materialTypeFull", "materialTypeMin", "materialTypeWidth"
    ];

    const materialOptions = [
        "Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"
    ];

    return (
        <Paper className="p-6 max-w-4xl mx-auto shadow-md">
            <Typography variant="h4" gutterBottom align="center">Material Specifications</Typography>

            <Grid item xs={12}><Divider /><Typography variant="h5">Customer Information</Typography></Grid>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                    <TextField size="small"
                        label="Customer"
                        value={materialSpecs.customer || ''}
                        onChange={(e) => handleChange("customer", e.target.value)}
                        fullWidth />
                </Grid>
                {["date", "reference"].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                    </Grid>
                ))}
            </Grid>

            <Tabs
                value={activeView}
                onChange={(e, newVal) => setActiveView(newVal)}
                indicatorColor="primary"
                textColor="primary"
                variant="scrollable"
                scrollButtons="auto"
                sx={{ mt: 4, mb: 2 }}
            >
                {Object.entries(viewConfigs).map(([key, { title }]) => (
                    <Tab key={key} value={key} label={title} />
                ))}
            </Tabs>

            <Grid container spacing={2}>
                {[...viewConfigs[activeView].fields, ...extraFieldsByView[activeView]].map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
                        {field.startsWith("materialType") ? (
                            <Grid container>
                                <Typography noWrap style={{ minWidth: 200 }}>{formatLabel(field)}</Typography>
                                <FormControl fullWidth size="small">
                                    <Select
                                        value={materialSpecs[field] || ''}
                                        onChange={(e) => handleChange(field, e.target.value)}
                                    >
                                        {materialOptions.map((option) => (
                                            <MenuItem key={option} value={option}>{option}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        ) : (
                            <TextField
                                size="small"
                                label={formatLabel(field)}
                                value={materialSpecs[field] || ''}
                                type="number"
                                onChange={(e) => handleChange(field, e.target.value)}
                                fullWidth
                            />
                        )}
                    </Grid>
                ))}
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
        </Paper>
    );
}
