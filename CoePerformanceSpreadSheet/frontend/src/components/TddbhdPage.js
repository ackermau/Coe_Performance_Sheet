import { useContext, useState, useEffect} from "react";
import {
    Paper, Typography, Grid, Divider, TextField, Tabs, Tab, FormControl, Select, MenuItem, InputLabel
} from "@mui/material";
import { ArrowDropDown } from "@mui/icons-material";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { useSharedMaterialView } from "../hooks/useSharedMaterialView";
import { RFQFormContext } from "../context/RFQFormContext";
import { TddbhdContext } from "../context/TddbhdContext";

const formatLabel = (label) => {
    return label
        .replace(/_/g, " ")
        .replace(/\b\w/g, (char) => char.toUpperCase());
};


const reelModels = ["CPR-040", "CPR-060", "CPR-080", "CPR-100", "CPR-200",
    "CPR-300", "CPR-400", "CPR-500", "CPR-600"];

const reelWidths = [42, 48, 54, 60, 66, 72];

const backplateDiameters = [27, 72];

const hydThreadingDrives = ["22 cu in (D-12689)", "38 cu in (D-13382)", "60 cu in (D-13374)", "60 cu in (D-13382)"];

const holdDownAssys = ["SD", "SD_MOTORIZED", "MD", "HD_Single", "HD_Dual", "XD", "XXD"];

const brakeModels = ["Single Stage", "Double Stage", "Triple Stage", "Failsafe - Single Stage", "Failsafe - Double Stage"];

const brakeQuantities = [1, 2, 3];

const materialTypeFields = [
    "materialTypeMax", "materialTypeFull", "materialTypeMin", "materialTypeWidth"
];

const materialOptions = [
    "Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"
];

export default function TddbhdPage() {
    const { rfqForm } = useContext(RFQFormContext);
    const { activeView, setActiveView, viewConfigs } = useSharedMaterialView();
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const { TddbhdData, setTddbhdData } = useContext(TddbhdContext);
    const [results, setResults] = useState(null);

    const handleChange = (field, value) => {
        const updated = { ...TddbhdData, [field]: value };
        setTddbhdData(updated);
        triggerBackendCalculation(updated);
    };

    const triggerBackendCalculation = async (payload) => {
        try {
            const response = await fetch("/api/material/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            setTddbhdData(prev => ({ ...prev, ...data }));
        } catch (err) {
            console.error("Backend calculation failed:", err);
        }
    };
    useEffect(() => {
        setTddbhdData(prev => ({
            ...prev,
            materialTypeMax: materialSpecs.materialTypeMax || prev.materialTypeMax,
            materialWidthMax: materialSpecs.coilWidthMax || prev.materialWidthMax,
            materialThicknessMax: materialSpecs.materialThicknessMax || prev.materialThicknessMax,
            yieldStrengthMax: materialSpecs.yieldStrengthMax || prev.yieldStrengthMax,

            materialTypeFull: materialSpecs.materialTypeFull || prev.materialTypeFull,
            materialWidthFull: materialSpecs.coilWidthFull || prev.materialWidthFull,
            materialThicknessFull: materialSpecs.materialThicknessFull || prev.materialThicknessFull,
            yieldStrengthFull: materialSpecs.yieldStrengthFull || prev.yieldStrengthFull,

            materialTypeMin: materialSpecs.materialTypeMin || prev.materialTypeMin,
            materialWidthMin: materialSpecs.coilWidthMin || prev.materialWidthMin,
            materialThicknessMin: materialSpecs.materialThicknessMin || prev.materialThicknessMin,
            yieldStrengthMin: materialSpecs.yieldStrengthMin || prev.yieldStrengthMin,

            materialTypeWidth: materialSpecs.materialTypeWidth || prev.materialTypeWidth,
            materialWidthWidth: materialSpecs.coilWidthWidth || prev.materialWidthWidth,
            materialThicknessWidth: materialSpecs.materialThicknessWidth || prev.materialThicknessWidth,
            yieldStrengthWidth: materialSpecs.yieldStrengthWidth || prev.yieldStrengthWidth
        }));
    }, [materialSpecs]);

    return (
        <Paper className="p-6 max-w-4xl mx-auto shadow-md">
            <Typography variant="h4" gutterBottom>TB/DB/HD Machine Simulation</Typography>

            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Reel Model & Material Properties</Typography>
            <Grid container spacing={2}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Reel Model</Typography>
                    <FormControl fullWidth size="small">
                        <Select value={TddbhdPage.reelModel}
                            onChange={(e) => handleChange("reel_model", e.target.value)}
                            name="reel_model">
                            {reelModels.map((model) => (
                                <MenuItem key={model} value={model}>{model}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Reel Width</Typography>
                    <FormControl fullWidth size="small">
                        <Select value={TddbhdPage.reelWidth}
                            onChange={(e) => handleChange("reel_width", e.target.value)}
                            name="reel_width">
                            {reelWidths.map((width) => (
                                <MenuItem key={width} value={width}>{width}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Backplate Diameter</Typography>
                    <FormControl fullWidth size="small">
                        <Select value={TddbhdPage.backplateDiameter}
                            onChange={(e) => handleChange("backplate_diameter", e.target.value)}
                            name="backplate_diameter">
                            {backplateDiameters.map((diameter) => (
                                <MenuItem key={diameter} value={diameter}>{diameter}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Tabs
                    value={activeView}
                    onChange={(e, newVal) => setActiveView(newVal)}
                    indicatorColor="primary"
                    textColor="primary"
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{ mt: 4, mb: 2 }} >
                    {Object.entries(viewConfigs).map(([key, { title }]) => (
                        <Tab key={key} value={key} label={title} />
                    ))}
                </Tabs>

                <Grid container spacing={2}>
                    {viewConfigs[activeView].fields.map((field) => (
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
                                    onChange={(e) => handleChange(field, e.target.value)}
                                    fullWidth
                                />
                            )}
                        </Grid>
                    ))}


                </Grid>
            </Grid>
        </Paper>
    );
}
