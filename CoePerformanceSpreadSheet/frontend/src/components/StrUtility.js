import { useState, useEffect, useContext } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, FormControl, Select, MenuItem, Button, Table, TableBody, TableRow, TableCell, CircularProgress
} from "@mui/material";
import { API_URL } from '../config';
import { StrUtilityContext } from "../context/StrUtilityContext";
import { MaterialSpecsContexr } from "../context/MaterialSpecsContext";

const formatLabel = (label) => label
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .replace(/([a-z])([A-Z])/g, "$1 $2");

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const payoffOptions = [
    "TOP", "BOTTOM"
];

const strModelOptions = [
    "CPPS-250", "CPPS-306", "CPPS-350", "CPPS-406", "CPPS-507", "SPGPS-810"
];

const strWidthOptions = [
    42, 48, 54, 60, 66, 72, 78
];

const horsepowerOptions = [
    40, 50, 60, 75, 100, 125
];

const feedRateOptions = [
    80, 100, 120, 140, 160, 200
];

const autoBrakeCompenOptions = [
    "YES", "NO"
];

const pulledFields = [
    "coilWeightCap", "coilID", "coilWidth", "thickness", "yieldStrength", "materialType"
];

const lookupFields = [
    "strRollDia", "pinchRollDia", "centerDist", "jackForceAvailable", "maxRollDepth", "modulus",
    "pinchRollGearTeeth", "pinchRollGearDP", "strRollGearTeeth", "strRollGearDP", "faceWidthTeeth", "contAngleTeeth"
];

const calculatedFields = [
    "requiredForce", "pinchRoll", "strRoll", "horsepowerRequired", "actualCoilWeight", "coilOD", "strTorque", "accelerationTorque", "brakeTorque"
];

const groupFields = {
    max: [...pulledFields.map(field => `${field}Max`), ...lookupFields.map(field => `${field}Max`), ...calculatedFields.map(field => `${field}Max`)],
    full: [...pulledFields.map(field => `${field}Full`), ...lookupFields.map(field => `${field}Full`), ...calculatedFields.map(field => `${field}Full`)],
    min: [...pulledFields.map(field => `${field}Min`), ...lookupFields.map(field => `${field}Min`), ...lookupFields.map(field => `${field}Min`), ...calculatedFields.map(field => `${field}Min`)],
    width: [...pulledFields.map(field => `${field}Width`), ...lookupFields.map(field => `${field}Width`), ...calculatedFields.map(field => `${field}Width`)]
};

export default function StrUtility() {
    const { subpageData, setSubpageData, activePage, setActivePage } = StrUtilityContext();

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);
    const [loading, setLoading] = useState(false);

    const sharedFields = [
        "payoff", "strModel", "strWidth", "horsepower", "feedRate", "autoBrakeCompensation", "acceleration"
    ];

    const getDefaultDataForGroup = (group) => {
        return {
            ...Object.fromEntries(
                groupFields[group].map(field => [field, materialSpecs?.[f] || ""])
            )
        };
    };

    useEffect(() => {
        const updateDataAndTriggerCalculations = async () => {
            if (!materialSpecs || !activePage) return;

            const sharedDefaults = {
                payoff: payoffOptions[0],
                strModel: strModelOptions[0],
                strWidth: strWidthOptions[0],
                horsepower: horsepowerOptions[0],
                feedRate: feedRateOptions[0],
                autoBrakeCompensation: autoBrakeCompenOptions[0],
                acceleration: 1
            }

            setSubpageData(prev => {
                const newData = {
                    page1: { ...getDefaultDataForGroup("max"), ...prev.page1 },
                    page2: { ...getDefaultDataForGroup("full"), ...prev.page2 },
                    page3: { ...getDefaultDataForGroup("min"), ...prev.page3 },
                    page4: { ...getDefaultDataForGroup("width"), ...prev.page4 }
                };
                return JSON.stringify(prev) !== JSON.stringify(newData) ? newData : prev; 
            });
        };

        updateDataAndTriggerCalculations();
    }, [materialSpecs, activePage]);

    const handleChange = (field, value) => {
        const updatedData = { ...prev };

        if (sharedFields.includes(field)) {
            // Update all pages if shared field
            Object.keys(prev).forEach(pageKey => {
                updatedData[pageKey] = {
                    ...prev[pageKey],
                    [field]: value
                };
            });
        } else {
            // Update only active page otherwise
            updatedData[activePage] = {
                ...prev[activePage],
                [field]: value
            };
        }

    }

    const buildStrUtilityPayload = (subpageData, pageKey) => {
        const capSuffix = capitalize(pageMapping[pageKey]);
        const data = subpageData[pageKey];
        return {
            coil_weight_cap: Number(materialSpecs[`coilWeightCap${capSuffix}`]),
            coil_id: Number(materialSpecs[`coilID${capSuffix}`]),
            coil_width: Number(materialSpecs[`coilWidth${capSuffix}`]),
            thickness: Number(materialSpecs[`thickness${capSuffix}`]),
            yield_strength: Number(materialSpecs[`yieldStrength${capSuffix}`]),
            material_type: materialSpecs[`materialType${capSuffix}`],
            selected_roll: materialSpecs.selected_roll,
            str_model: data.strModel,
            str_width: data.strWidth,
            horsepower: data.horsepower,
            feed_rate: data.feedRate,
            auto_brake_compensation: data.autoBrakeCompensation,
            acceleration: data.acceleration,
        };
    };

    return (
        <Paper sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom>
                Straightener Selection Utility - {`${capSuffix}`}
            </Typography>
            <Divider sx={{ my: 2 }} />

            {/* Shared Fields */}
            <Typography variant="h6">Str Utility & Properties</Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Payoff</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].payoff || ""}
                            onChange={(e) => handleChange("payoff", e.target.value)}
                            name="payoff"
                            disabled={sharedFields.includes("payoff") && activePage !== "page1"}
                        >
                            {payoffOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                    </Select>
                </FormControl>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Str Model</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].strModel || ""}
                            onChange={(e) => handleChange("strModel", e.target.value)}
                            name="strModel"
                            disabled={sharedFields.includes("strModel") && activePage !== "page1"}
                        >
                            {strModelOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Str Width</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].strWidth || ""}
                            onChange={(e) => handleChange("strWidth", e.target.value)}
                            name="strWidth"
                            disabled={sharedFields.includes("strWidth") && activePage !== "page1"}
                        >
                            {strWidthOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Horsepower</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].horsepower || ""}
                            onChange={(e) => handleChange("horsepower", e.target.value)}
                            name="horsepower"
                            disabled={sharedFields.includes("horsepower") && activePage !== "page1"}
                        >
                            {horsepowerOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Acceleration</Typography>
                    <TextField size="small"
                        value={subpageData[activePage].acceleration || ""}
                        onChange={(e) => handleChange("acceleration", e.target.value)}
                        name="acceleration"
                        type="number"
                        disabled={sharedFields.includes("acceleration") && activePage !== "page1"}
                    />
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Feed Rate</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].feedRate || ""}
                            onChange={(e) => handleChange("feedRate", e.target.value)}
                            name="feedRate"
                            disabled={sharedFields.includes("feedRate") && activePage !== "page1"}
                        >
                            {feedRateOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography nowrap style={{ minWidth: 200 }}>Auto Brake Compensation</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].autoBrakeCompensation || ""}
                            onChange={(e) => handleChange("autoBrakeCompensation", e.target.value)}
                            name="autoBrakeCompensation"
                            disabled={sharedFields.includes("autoBrakeCompensation") && activePage !== "page1"}
                        >
                            {autoBrakeCompenOptions.map((selected) => (
                                <MenuItem key={selected} value={selected}>
                                    {selected}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Material Specs</Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                {pulledFields.map((field) => (
                    <Grid item xs={12} md={4} key={field}>
                        <Typography nowrap style={{ minWidth: 200 }}>{formatLabel(field)}</Typography>
                        <TextField size="small"
                            value={subpageData[activePage][field] || ""}
                            onChange={(e) => handleChange(field, e.target.value)}
                            name={field}
                            disabled={pulledFields.includes(field) && activePage !== "page1"}
                        />
                    </Grid>
                ))}
            </Grid>

            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Lookup Values</Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                {lookupFields.map((field) => (
                    <Grid item xs={12} md={4} key={field}>
                        <Typography nowrap style={{ minWidth: 200 }}>{formatLabel(field)}</Typography>
                        <TextField size="small"
                            value={subpageData[activePage][field] || ""}
                            onChange={(e) => handleChange(field, e.target.value)}
                            name={field}
                            disabled={lookupFields.includes(field) && activePage !== "page1"}
                        />
                    </Grid>
                ))}
            </Grid>

            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Calculated Values</Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                {calculatedFields.map((field) => (
                    <Grid item xs={12} md={4} key={field}>
                        <Typography nowrap style={{ minWidth: 200 }}>{formatLabel(field)}</Typography>
                        <TextField size="small"
                            value={subpageData[activePage][field] || ""}
                            onChange={(e) => handleChange(field, e.target.value)}
                            name={field}
                            disabled={calculatedFields.includes(field) && activePage !== "page1"}
                        />
                    </Grid>
                ))}
            </Grid>
        </Paper>
    );
}