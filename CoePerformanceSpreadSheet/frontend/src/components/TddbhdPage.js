import { useState, useEffect, useContext } from "react";
import {
    Paper,
    Typography,
    Grid,
    Divider,
    TextField,
    FormControl,
    Select,
    MenuItem,
    Button,
    Table,
    TableBody,
    TableRow,
    TableCell
} from "@mui/material";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { RFQFormContext } from "../context/RFQFormContext";
import { API_URL } from '../config';

const formatLabel = (label) => {
    return label
        .replace(/_/g, " ")
        .replace(/\b\w/g, (char) => char.toUpperCase())
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/\s*(Max|Full|Min|Width)$/i, "");
};

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const reelModels = [
    "CPR-040", "CPR-060", "CPR-080", "CPR-100",
    "CPR-200", "CPR-300", "CPR-400", "CPR-500", "CPR-600"
];

const reelWidths = [42, 48, 54, 60, 66, 72];

const backplateDiameters = [27, 72];

const materialOptions = [
    "Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel",
    "Dual Phase", "Cold Rolled Steel", "Stainless Steel",
    "Titanium", "Brass", "Beryl Copper"
];

const baseMaterialFields = [
    "materialType", "coilWidth", "materialThickness", "yieldStrength",
    "coilWeight", "coilID", "coilOD"
];

const extraFields = [
    "thickness", "density", "calcWeight", "maxWeight", "tensionTorque", "decel", "y",
    "M", "My", "friction", "airPressure", "maxPsi", "holddownPressure",
    "holddownForceFactor", "holddownMinWidth", "brakeQty", "noBrakepads",
    "brakeDist", "pressForceRequired", "pressForceHolding",
    "holddownMatrixLabel", "webTensionPsi", "webTensionLbs",
    "dispReelMtr", "torqueAtMandrel", "rewindTorque",
    "holdDownForceRequired", "holdDownForceAvailable",
    "minMaterialWidth", "torqueRequired",
    "failsafeDoubleStage", "failsafeHoldingForce"
];

const groupFields = {
    max: [...baseMaterialFields.map(f => `${f}Max`), ...extraFields.map(f => `${f}Max`)],
    full: [...baseMaterialFields.map(f => `${f}Full`), ...extraFields.map(f => `${f}Full`)],
    min: [...baseMaterialFields.map(f => `${f}Min`), ...extraFields.map(f => `${f}Min`)],
    width: [...baseMaterialFields.map(f => `${f}Width`), ...extraFields.map(f => `${f}Width`)]
};

const brakeQtyOptions = ["1", "2", "3"];

const getDefaultDataForGroup = (group, materialSpecs) => {
    return {
        reelModel: reelModels[0],
        reelWidth: reelWidths[0],
        backplateDiameter: backplateDiameters[0],
        typeOfLine: "PULLOFF",
        driveTorque: "",
        reelDriveTQEmpty: "",

        maxCoilWeight: materialSpecs.maxCoilWeight,

        ...groupFields[group].reduce((acc, field) => {
            acc[field] = materialSpecs?.[field] || "";
            return acc;
        }, {})
    };
};

const CalculatedField = ({ label, value }) => (
    <>
        <Grid item xs={6} sm={4}>
            <Typography variant="body1">{label}</Typography>
        </Grid>
        <Grid item xs={6} sm={8}>
            <TextField
                value={value}
                variant="outlined"
                size="small"
                fullWidth
                InputProps={{ readOnly: true }}
            />
        </Grid>
    </>
);

export default function TddbhdPage() {
    const { rfqForm } = useContext(RFQFormContext);
    const { materialSpecs } = useContext(MaterialSpecsContext);

    const pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };

    const [subpageData, setSubpageData] = useState({
        page1: getDefaultDataForGroup("max", materialSpecs),
        page2: getDefaultDataForGroup("full", materialSpecs),
        page3: getDefaultDataForGroup("min", materialSpecs),
        page4: getDefaultDataForGroup("width", materialSpecs)
    });

    const [activePage, setActivePage] = useState("page1");

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);

    useEffect(() => {
        setSubpageData(prev => ({
            page1: { ...getDefaultDataForGroup("max", materialSpecs), ...prev.page1 },
            page2: { ...getDefaultDataForGroup("full", materialSpecs), ...prev.page2 },
            page3: { ...getDefaultDataForGroup("min", materialSpecs), ...prev.page3 },
            page4: { ...getDefaultDataForGroup("width", materialSpecs), ...prev.page4 },
        }));
        const payload = buildTddbhdPayload();
        console.log("Sending payload:", payload);
        triggerBackendCalculation(payload);
    }, [materialSpecs]);

    const handleChange = (field, value) => {
        setSubpageData(prev => ({
            ...prev,
            [activePage]: { ...prev[activePage], [field]: value }
        }));
        const payload = buildTddbhdPayload();
        console.log("Sending payload:", payload);
        triggerBackendCalculation(payload);
    };

    const buildTddbhdPayload = () => {
        const data = subpageData[activePage];

        return {
            type_of_line: data.typeOfLine,
            drive_torque: Number(data.driveTorque) || 0,
            reel_drive_tqempty: Number(data.reelDriveTQEmpty) || 0,
            yield_strength: Number(data[`yieldStrength${capSuffix}`]) || 0,
            thickness: Number(data[`materialThickness${capSuffix}`]) || 0,
            width: Number(data[`coilWidth${capSuffix}`]) || 0,
            coil_id: Number(data[`coilID${capSuffix}`]) || 0,
            coil_od: Number(data[`coilOD${capSuffix}`]) || 0,
            coil_weight: Number(data[`calcWeight${capSuffix}`]) || 0,
            density: Number(data[`density${capSuffix}`]) || 0,
            tension_torque: Number(data[`tensionTorque${capSuffix}`]) || 0,
            decel: Number(data[`decel${capSuffix}`]) || 0,
            y: Number(data[`y${capSuffix}`]) || 0,
            M: Number(data[`M${capSuffix}`]) || 0,
            My: Number(data[`My${capSuffix}`]) || 0,
            friction: Number(data[`friction${capSuffix}`]) || 0,
            air_pressure: Number(data[`airPressure${capSuffix}`]) || 0,
            max_psi: Number(data[`maxPsi${capSuffix}`]) || 0,
            holddown_pressure: Number(data[`holddownPressure${capSuffix}`]) || 0,
            holddown_force_factor: Number(data[`holddownForceFactor${capSuffix}`]) || 0,
            holddown_min_width: Number(data[`holddownMinWidth${capSuffix}`]) || 0,
            brake_qty: Number(data[`brakeQty${capSuffix}`]) || 0,
            no_brakepads: Number(data[`noBrakepads${capSuffix}`]) || 0,
            brake_dist: Number(data[`brakeDist${capSuffix}`]) || 0,
            press_force_required: Number(data[`pressForceRequired${capSuffix}`]) || 0,
            press_force_holding: Number(data[`pressForceHolding${capSuffix}`]) || 0,
            holddown_matrix_label: data[`holddownMatrixLabel${capSuffix}`] || "",
            materialType: data[`materialType${capSuffix}`] || "COLD ROLLED STEEL",
            reel_model: data.reelModel || "",

            max_weight: data.maxCoilWeight || 0,
        };
    };

    const snakeToCamel = (str) => {
        return str.replace(/(_\w)/g, m => m[1].toUpperCase());
    };

    const triggerBackendCalculation = async (payload) => {
        try {
            const response = await fetch(`${API_URL}/api/tddbhd/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Backend calculation error:", errorData);
                return;
            }
            const data = await response.json();
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
                [activePage]: { ...prev[activePage], ...transformedData }
            }));
        } catch (err) {
            console.error("Backend calculation failed:", err);
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
        <Paper className="p-6 max-w-4xl mx-auto shadow-md">
            <Typography variant="h4" gutterBottom>
                TB/DB/HD Machine Simulation
            </Typography>
            <Divider sx={{ my: 2 }} />

            {/* Common Reel Fields */}
            <Typography variant="h6">Reel Model & Properties</Typography>
            <Grid container spacing={2}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Reel Model</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].reelModel}
                            onChange={(e) => handleChange("reelModel", e.target.value)}
                            name="reel_model"
                        >
                            {reelModels.map((model) => (
                                <MenuItem key={model} value={model}>
                                    {model}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Reel Width</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].reelWidth}
                            onChange={(e) => handleChange("reelWidth", e.target.value)}
                            name="reelWidth"
                        >
                            {reelWidths.map((width) => (
                                <MenuItem key={width} value={width}>
                                    {width}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Backplate Diameter</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].backplateDiameter}
                            onChange={(e) => handleChange("backplateDiameter", e.target.value)}
                            name="backplateDiameter"
                        >
                            {backplateDiameters.map((diameter) => (
                                <MenuItem key={diameter} value={diameter}>
                                    {diameter}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid item xs={6} md={4}>
                <Typography noWrap style={{ minWidth: 200 }}>Brake Quantity</Typography>
                <FormControl fullWidth size="small">
                    <Select
                        value={subpageData[activePage][`brakeQty${capSuffix}`] || ""}
                        onChange={(e) => handleChange(`brakeQty${capSuffix}`, e.target.value)}
                        name={`brakeQty${capSuffix}`}
                    >
                        {brakeQtyOptions.map((option) => (
                            <MenuItem key={option} value={option}>
                                {option}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Air Pressure Available</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage][`airPressure${capSuffix}`] || ""}
                        onChange={(e) => handleChange(`airPressure${capSuffix}`, e.target.value)}
                        fullWidth
                    />
                </Grid>

                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Required Deceleration Rate</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage][`decel${capSuffix}`] || ""}
                        onChange={(e) => handleChange(`decel${capSuffix}`, e.target.value)}
                        fullWidth
                    />
                </Grid>
            </Grid>

            {/* Material Fields for the current subpage */}
            <Typography variant="h6" sx={{ mt: 2 }}>
                {pages.find((p) => p.key === activePage)?.title} Material Properties
            </Typography>
            <Grid container spacing={1} xs={12} sx={{ mt: 1 }}>
                {currentGroupFields.map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        {field.startsWith("materialType") ? (
                            <Grid container spacing={1}>
                                <Grid item xs={12}>
                                    <Typography noWrap style={{ minWidth: 200 }}>
                                        {formatLabel(field)}
                                    </Typography>
                                </Grid>
                                <Grid item xs={12}>
                                    <FormControl fullWidth size="small">
                                        <Select
                                            value={subpageData[activePage][field] || ""}
                                            onChange={(e) => handleChange(field, e.target.value)}
                                        >
                                            {materialOptions.map((option) => (
                                                <MenuItem key={option} value={option}>
                                                    {option}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </Grid>
                        ) : (
                            <CalculatedField
                                label={formatLabel(field)}
                                value={subpageData[activePage][field] || ""} />
                        )}
                    </Grid>
                ))}
            </Grid>

            <Divider sx={{ my: 2 }} />

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
