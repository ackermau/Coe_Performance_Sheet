import { useState, useEffect, useContext } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, FormControl, Select, MenuItem, Button, Table, TableBody, TableRow, TableCell, CircularProgress
} from "@mui/material";
import { API_URL } from '../config';
import { StrUtilityContext } from "../context/StrUtilityContext";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";

const formatLabel = (label) => {
    const suffixes = ["Max", "Min", "Full", "Width"];
    const suffixRegex = new RegExp(`(${suffixes.join("|")})$`, "i");

    // Remove suffix if present
    const stripped = label.replace(suffixRegex, "");

    // Then apply formatting
    return stripped
        .replace(/_/g, " ")
        .replace(/\b\w/g, (char) => char.toUpperCase())
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .trim();
};

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
    "coilID", "coilWidth", "materialThickness", "yieldStrength", "materialType"
];

const calculatedFields = [
    "requiredForce", "pinchRollDia", "strRollDia", "pinchRollReqTorque", "pinchRollRatedTorque", "strRollReqTorque", "strRollRatedTorque", "horsepowerRequired", 
    "centerDist", "jackForceAvailable", "maxRollDepth", "modulus", "pinchRollTeeth", "pinchRollDP", "strRollTeeth", "strRollDP", "contAngle" ,
    "actualCoilWeight", "coilOD", "strTorque", "accelerationTorque", "brakeTorque",
];

const pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };

const groupFields = {
    max: [...pulledFields.map(field => `${field}Max`), ...calculatedFields.map(field => `${field}Max`)],
    full: [...pulledFields.map(field => `${field}Full`), ...calculatedFields.map(field => `${field}Full`)],
    min: [...pulledFields.map(field => `${field}Min`), ...calculatedFields.map(field => `${field}Min`)],
    width: [...pulledFields.map(field => `${field}Width`), ...calculatedFields.map(field => `${field}Width`)]
};

export default function StrUtility() {
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext(StrUtilityContext);

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);
    const [loading, setLoading] = useState(false);

    const sharedFields = [
        "payoff", "strModel", "strWidth", "horsepower", "feedRate", "autoBrakeCompensation", "acceleration"
    ];

    const getDefaultDataForGroup = (group, sharedFields, materialSpecs) => {
        return {
            ...sharedFields,
            ...Object.fromEntries(
                groupFields[group].map(field => [field, materialSpecs?.[field] || ""])
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
                acceleration: 1,
                maxCoilWeight: materialSpecs.maxCoilWeight
            }

            setSubpageData(prev => {
                const newData = {
                    page1: { ...getDefaultDataForGroup("max", sharedDefaults, materialSpecs), ...prev.page1 },
                    page2: { ...getDefaultDataForGroup("full", sharedDefaults, materialSpecs), ...prev.page2 },
                    page3: { ...getDefaultDataForGroup("min", sharedDefaults, materialSpecs), ...prev.page3 },
                    page4: { ...getDefaultDataForGroup("width", sharedDefaults, materialSpecs), ...prev.page4 }
                };
                return JSON.stringify(prev) !== JSON.stringify(newData) ? newData : prev; 
            });
        };

        updateDataAndTriggerCalculations();
    }, [materialSpecs, activePage]);

    const handleChange = (field, value) => {
        setSubpageData(prev => {
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

            try {
                Object.keys(updatedData).forEach(pageKey => {
                    const payload = buildStrUtilityPayload(updatedData, pageKey);
                    console.log("Payload being sent:", payload);
                    triggerBackendCalculation(payload, pageKey);
                });
            }
            catch (error) {
                console.error("Error updating data:", error);
            }

            return updatedData;
        });
    };

    const buildStrUtilityPayload = (subpageData, pageKey) => {
        const capSuffix = capitalize(pageMapping[pageKey]);
        const data = subpageData[pageKey];
        return {
            max_coil_weight: parseFloat(materialSpecs.maxCoilWeight) || 0,
            coil_id: parseFloat(materialSpecs[`coilID${capSuffix}`]) || 0,
            coil_od: parseFloat(materialSpecs[`coilOD${capSuffix}`]) || 0,
            coil_width: parseFloat(materialSpecs[`coilWidth${capSuffix}`]) || 0,
            material_thickness: parseFloat(materialSpecs[`materialThickness${capSuffix}`]) || 0,
            yield_strength: parseFloat(materialSpecs[`yieldStrength${capSuffix}`]) || 0,
            material_type: materialSpecs[`materialType${capSuffix}`] || "",

            selected_roll: materialSpecs.selectedRoll || "",
            str_model: data.strModel || "",
            str_width: parseFloat(data.strWidth) || 0,
            horsepower: parseFloat(data.horsepower) || 0,

            feed_rate: parseFloat(data.feedRate) || 0,
            auto_brake_compensation: data.autoBrakeCompensation || "",
            acceleration: parseFloat(data.acceleration) || 0,
            num_str_rolls: Number(data.numStrRolls) || 0,
        };
    };

    const snakeToCamel = (str) => {
        return str.replace(/(_\w)/g, m => m[1].toUpperCase());
    };

    const triggerBackendCalculation = async (payload, pageKey) => {
        try {
            const response = await fetch(`${API_URL}/api/str_utility/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                throw new Error("Failed to fetch data");
                console.error("Backend calculation error:", errorData);
                return;
            }
            const data = await response.json();
            const capSuffix = capitalize(pageMapping[pageKey]);
            console.log("Backend response data:", data);
            // Transform result keys: convert each from snake_case to camelCase then append current page suffix (e.g., 'Max')
            const transformedData = {};
            for (const key in data) {
                const camelKey = snakeToCamel(key); // converts "web_tension_psi" to "webTensionPsi"
                transformedData[`${camelKey}${capSuffix}`] = data[key];
            }
            console.log("Transformed data:", transformedData);
            setSubpageData(prev => ({
                ...prev,
                [pageKey]: { ...prev[pageKey], ...transformedData }
            }));
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    };

    const pages = [
        { key: "page1", title: "Max" },
        { key: "page2", title: "Full" },
        { key: "page3", title: "Min" },
        { key: "page4", title: "Width" }
    ];

    const goToPreviousPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex > 0) setActivePage(pages[currentIndex - 1].key);
    };

    const goToNextPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex < pages.length - 1) setActivePage(pages[currentIndex + 1].key);
    };

    const currentGroup = pageMapping[activePage];
    const currentGroupFields = groupFields[currentGroup];

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
                    <Typography noWrap style={{ minWidth: 200 }}>Payoff</Typography>
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
                    <Typography noWrap style={{ minWidth: 200 }}>Str Model</Typography>
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
                    <Typography noWrap style={{ minWidth: 200 }}>Str Width</Typography>
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

                <Grid item xs={12} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Number of Str Rolls</Typography>
                    <TextField size="small"
                        value={subpageData[activePage].numStrRolls || ""}
                        onChange={(e) => handleChange("numStrRolls", e.target.value)}
                        name="numStrRolls"
                        type="number"
                        disabled={sharedFields.includes("numStrRolls") && activePage !== "page1"}
                    />
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Horsepower</Typography>
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
                    <Typography noWrap style={{ minWidth: 200 }}>Acceleration</Typography>
                    <TextField size="small"
                        value={subpageData[activePage].acceleration || ""}
                        onChange={(e) => handleChange("acceleration", e.target.value)}
                        name="acceleration"
                        type="number"
                        disabled={sharedFields.includes("acceleration") && activePage !== "page1"}
                    />
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Feed Rate</Typography>
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
                    <Typography noWrap style={{ minWidth: 200 }}>Auto Brake Compensation</Typography>
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

            {/* Calculated Fields */}
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6">Calculated Values</Typography>
            <Grid container spacing={1} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Max Coil Weight</Typography>
                    <TextField size="small"
                        value={subpageData[activePage].maxCoilWeight || ""}
                        onChange={(e) => handleChange("maxCoilWeight", e.target.value)}
                        name="maxCoilWeight"
                        type="number"
                        disabled={sharedFields.includes("maxCoilWeight") && activePage !== "page1"}
                    />
                </Grid>

                {currentGroupFields.map((field) => (
                    <Grid item xs={12} md={6} key={field}>
                        <Typography noWrap style={{ minWidth: 200 }}>{formatLabel(field)}</Typography>
                        <TextField size="small"
                            value={subpageData[activePage][field] || ""}
                            onChange={(e) => handleChange(field, e.target.value)}
                            name={field}
                            disabled={currentGroupFields.includes(field) && activePage !== "page1"}
                        />
                    </Grid>
                ))}
            </Grid>

            {/* Navigation Buttons */}
            <Grid
                container
                spacing={2}
                justifyContent="space-between"
                alignItems="center"
                sx={{ mt: 4 }}
            >
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={goToPreviousPage}
                        disabled={activePage === "page1"}
                    >
                        Back
                    </Button>
                </Grid>
                <Grid item>
                    <Typography variant="subtitle1">
                        {pages.find((p) => p.key === activePage)?.title}
                    </Typography>
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={goToNextPage}
                        disabled={activePage === "page4"}
                    >
                        Next
                    </Button>
                </Grid>
            </Grid>
        </Paper>
    );
}