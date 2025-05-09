import { useState, useEffect, useContext } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, FormControl, Select, MenuItem, Button, Table, TableBody, TableRow, TableCell, CircularProgress
} from "@mui/material";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { RFQFormContext } from "../context/RFQFormContext";
import { TddbhdContext } from "../context/TddbhdContext";
import { ReelDriveContext } from "../context/ReelDriveContext";
import { API_URL } from '../config';

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

const knownAcronyms = ["od", "dp", "id", "hp", "rpm"];

const green = "#4caf50";
const red = "#f44336";

const reelModels = [
    "CPR-040", "CPR-060", "CPR-080", "CPR-100",
    "CPR-200", "CPR-300", "CPR-400", "CPR-500", "CPR-600"
];

const reelWidths = [42, 48, 54, 60, 66, 72];

const backplateDiameterOptions = [27, 72];

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
    "calculatedCoilWeight", "holddownPressure",
    "webTensionPsi", "webTensionLbs",
    "dispReelMtr", "torqueAtMandrel", "rewindTorque",
    "holdDownForceRequired", "holdDownForceAvailable",
    "minMaterialWidth", "torqueRequired",
    "brakePressHoldingForce", "brakePressRequired"
];

const typeOfLineOptions = [
    "Compact", "Compact CTL", "Conventional", "Conventional CTL", "Pull Through", "Pull Through Compact",
    "Pull Through CTL", "Feed", "Feed-Pull Through", "Feed-Pull Through-Shear", "Feed-Shear",
    "Straightener", "Straightener-Reel Combination", "Reel-Motorized", "Reel-Pull Off",
    "Threading Table", "Other"
];

const horsepowerOptions = [5, 7.5, 10, 15, 20];

const pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };
const brakeModelOptions = ["Single Stage", "Double Stage", "Triple Stage", "Failsafe - Single Stage", "Failsafe - Double Stage"];
const airClutchOptions = ["Yes", "No"];
const hydThreadingDriveOptions = ["22 cu in (D-12689)", "38 cu in (D-13374)", "60 cu in (D-13374)", "60 cu in (D-13382)"];
const holdDownAssyOptions = ["SD", "SD_MOTORIZED", "MD", "HD_SINGLE", "HD_DUAL", "XD", "XXD"];
const cylinderOptions = ["Hydraulic"];

const brakeQtyOptions = ["1", "2", "3"];

const groupFields = {
    max: [...baseMaterialFields.map(f => `${f}Max`), ...extraFields.map(f => `${f}Max`)],
    full: [...baseMaterialFields.map(f => `${f}Full`), ...extraFields.map(f => `${f}Full`)],
    min: [...baseMaterialFields.map(f => `${f}Min`), ...extraFields.map(f => `${f}Min`)],
    width: [...baseMaterialFields.map(f => `${f}Width`), ...extraFields.map(f => `${f}Width`)]
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
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext(TddbhdContext);
    const { reelDriveData, setReelDriveData } = useContext(ReelDriveContext);

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);
    const [loading, setLoading] = useState(false);

    const sharedFields = [
        "reelModel",
        "reelWidth",
        "backplateDiameter",
        "typeOfLine",
        "horsepower",
        "reelDriveTQEmpty",
        "emptyHorsepower",
        "fullHorsepower",
        "brakeQty",
        "brakeModel",
        "airClutch",
        "hydThreadingDrive",
        "holdDownAssy",
        "cylinder",
        "airPressure",
        "decel",
        "friction",
    ];

    const getDefaultDataForGroup = (group, sharedDefaults, materialSpecs) => {
        return {
            ...sharedDefaults,
            ...Object.fromEntries(
                groupFields[group].map(f => [f, materialSpecs?.[f] || ""])
            )
        };
    };

    useEffect(() => {
        const updateDataAndTriggerCalculations = async () => {
            if (!materialSpecs || !activePage) return;

            const sharedDefaults = {
                reelModel: reelModels[0],
                reelWidth: reelWidths[0],
                backplateDiameter: backplateDiameterOptions[0],
                typeOfLine: typeOfLineOptions[0],
                horsepower: horsepowerOptions[0],
                reelDriveTQEmpty: "",
                emptyHorsepower: "",
                fullHorsepower: "",
                brakeQty: brakeQtyOptions[0],
                brakeModel: brakeModelOptions[0],
                airClutch: airClutchOptions[0],
                hydThreadingDrive: hydThreadingDriveOptions[0],
                holdDownAssy: holdDownAssyOptions[0],
                cylinder: cylinderOptions[0],
                airPressure: "",
                decel: "",
                friction: "",
                maxCoilWeight: materialSpecs.maxCoilWeight,
            };

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
                    const form = buildReelDriveForm(updatedData, pageKey);
                    if (validateForm(form)) {
                        console.log("Sending form:", form);
                        triggerReelDriveCalculation(form, pageKey);
                    } else {
                        console.warn("Form invalid on init load, not sending.");
                    }

                    const payload = buildTddbhdPayload(updatedData, pageKey);
                    if (validatePayload(payload)) {
                        console.log("Sending payload:", payload);
                        triggerBackendCalculation(payload, pageKey);
                    } else {
                        console.warn("Payload invalid on init load, not sending.");
                    }
                });
            } catch (err) {
                console.error("ReelDrive calculation failed:", err);
            }

            return updatedData;
        });
    };

    const passConditions = {
        rewindTorque: (v) => v != null && v !== 0 && v >= 100,
        coilWidth: (v) => v != null && v !== 0 && v >= Number(subpageData[activePage][`materialThickness${capSuffix}`]),
        holdDownForceRequired: (v) => v != null && v !== 0 && v <= Number(subpageData[activePage][`holdDownForceAvailable${capSuffix}`]),
        brakePressRequired: (v) => v != null && v !== 0 && v <= Number(subpageData[activePage][`airPressure`]),
        torqueRequired: (v) => v != null && v !== 0 && v <= Number(subpageData[activePage][`brakePressHoldingForce${capSuffix}`])
    };

    const evaluateCondition = (field, pageKey) => {
        const suffix = capitalize(pageMapping[pageKey]);
        const value = Number(subpageData[pageKey]?.[`${field}${suffix}`]);
        const fieldCondition = passConditions[field];

        if (typeof fieldCondition === "function") {
            return fieldCondition(value);
        } else if (typeof fieldCondition === "object" && fieldCondition[suffix]) {
            return fieldCondition[suffix](value);
        }
        return true; // If no condition is defined
    };

    const validateField = (requiredFields, payload) => {
        for (const field of requiredFields) {
            if (
                payload[field] === undefined ||
                payload[field] === null ||
                payload[field] === "" ||
                (typeof payload[field] === "number" && isNaN(payload[field]))
            ) {
                console.warn(`Validation failed: Missing or invalid ${field}`);
                return false;
            }
        }
        return true;
    }

    const validateForm = (form) => {
        const requiredFields = [
            "model", "material_type", "coil_weight", "coil_id",
            "coil_od", "reel_width", "backplate_diameter", "motor_hp",
            "type_of_line", "required_max_fpm"
        ];

        if (!validateField(requiredFields, form)) {
            console.warn("Form validation failed");
            return false;
        }
        return true;
    }

    const validatePayload = (payload) => {
        const requiredFields = [
            "type_of_line", "reel_drive_tqempty", "yield_strength",
            "thickness", "width", "coil_id", "coil_od", "coil_weight",
            "decel", "friction", "air_pressure", "holddown_pressure",
            "brake_qty", "brake_model", "cylinder", "hold_down_assy",
            "hyd_threading_drive", "air_clutch", "material_type", "reel_model"
        ];

        if (!validateField(requiredFields, payload)) {
            console.warn("Payload validation failed");
            return false;
        }
        return true;
    };

    const snakeToCamel = (str) => {
        return str.split('_').map((word, index) => {
            if (index === 0) return word;
            return knownAcronyms.includes(word.toLowerCase())
                ? word.toUpperCase()
                : word.charAt(0).toUpperCase() + word.slice(1);
        }).join('');
    };

    const buildTddbhdPayload = (subpageData, pageKey) => {
        const capSuffix = capitalize(pageMapping[pageKey]);
        const data = subpageData[pageKey];
        return {
            type_of_line: data.typeOfLine,
            reel_drive_tqempty: Number(data.reelDriveTQEmpty || 0),
            motor_hp: parseFloat(data.horsepower) || 0,
            empty_hp: parseFloat(data.emptyHorsepower) || 0,
            full_hp: parseFloat(data.fullHorsepower) || 0,

            yield_strength: Number(materialSpecs[`yieldStrength${capSuffix}`]) || 0,
            thickness: Number(materialSpecs[`materialThickness${capSuffix}`]) || 0,
            width: Number(materialSpecs[`coilWidth${capSuffix}`]) || 0,
            coil_id: Number(materialSpecs[`coilID${capSuffix}`]) || 0,
            coil_od: Number(materialSpecs[`coilOD${capSuffix}`]) || 0,
            coil_weight: materialSpecs.maxCoilWeight || 0,

            decel: parseFloat(data.decel) || 0,
            friction: parseFloat(data.friction) || 0,
            air_pressure: parseFloat(data.airPressure) || 0,
            holddown_pressure: Number(data[`holddownPressure${capSuffix}`]) || 0,

            brake_qty: Number(data[`brakeQty`]) || 1,
            brake_model: data[`brakeModel`] || "",

            cylinder: data[`cylinder`] || "",
            hold_down_assy: data[`holdDownAssy`] || "",
            hyd_threading_drive: data[`hydThreadingDrive`] || "",
            air_clutch: data[`airClutch`] || "",

            material_type: materialSpecs[`materialType${capSuffix}`] || "Cold Rolled Steel",
            reel_model: data.reelModel || "",
        };
    };

    const buildReelDriveForm = (subpageData, pageKey) => {
        const data = subpageData[pageKey];
        return {
            date: materialSpecs.date,
            customer: materialSpecs.customer,
            reference: materialSpecs.reference,

            model: data.reelModel,
            material_type: materialSpecs.materialTypeMax,
            coil_weight: parseFloat(materialSpecs.coilWeightMax),
            coil_id: parseFloat(materialSpecs.coilIDMax),
            coil_od: parseFloat(materialSpecs.coilODMax),
            reel_width: parseFloat(materialSpecs.coilWidthMax),
            backplate_diameter: data.backplateDiameter,
            motor_hp: data.horsepower,
            type_of_line: materialSpecs.lineType,
            required_max_fpm: parseFloat(materialSpecs.requiredMaxFPMMax),
        };
    };

    const triggerBackendCalculation = async (payload, pageKey) => {
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
        } catch (err) {
            console.error("Tddbhd backend calculation failed:", err);
        }
    };

    const triggerReelDriveCalculation = async (form, pageKey) => {
        try {
            const response = await fetch(`${API_URL}/api/reel_drive/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });
            if (!response.ok) {
                const errorData = await response.json();
                console.error("ReelDrive calculation error:", errorData);
                return;
            }
            const data = await response.json();
            console.log("ReelDrive response data:", data);
            setSubpageData(prev => ({
                ...prev,
                [pageKey]: {
                    ...prev[pageKey],
                    reelDriveTQEmpty: (data?.torque?.empty || 0).toFixed(2),
                    emptyHorsepower: (data?.hp_req?.empty || 0).toFixed(2),
                    fullHorsepower: (data?.hp_req?.full || 0).toFixed(2)
                }
            }));
        } catch (err) {
            console.error("ReelDrive calculation failed:", err);
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

    const renderTextField = (field) => (
        <Grid item xs={12} sm={6} key={field}>
            <TextField
                label={formatLabel(field)}
                value={subpageData[activePage][field] || ""}
                type="text"
                onChange={(e) => handleChange(field, e.target.value)}
                fullWidth
                size="small"
            />
        </Grid>
    );

    const renderNumberField = (field) => (
        <Grid item xs={12} sm={6} key={field}>
            <Typography noWrap style={{ minWidth: 200 }}>field</Typography>
            <TextField
                label={formatLabel(field)}
                value={subpageData[activePage][field] || ""}
                type="number"
                onChange={(e) => handleChange(field, e.target.value)}
                fullWidth
                size="small"
            />
        </Grid>
    );

    const renderSelect = (field, options) => (
        <Grid item xs={12} sm={6} key={field}>
            <FormControl fullWidth size="small">
                <Typography gutterBottom>{formatLabel(field)}</Typography>
                <Select
                    value={subpageData[activePage][field] || options[0]}
                    onChange={(e) => handleChange(field, e.target.value)}
                >
                    {options.map((opt) => (
                        <MenuItem key={opt} value={opt}>{opt}</MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Grid>
    );

    return (
        <Paper sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom>
                TB/DB/HD Machine Simulation - {`${capSuffix}`}
            </Typography>
            <Divider sx={{ my: 2 }} />

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

            {/* Common Reel Fields */}
            <Typography variant="h6">Reel Model & Properties</Typography>
            <Grid container spacing={2}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Reel Model</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].reelModel || ""}
                            onChange={(e) => handleChange("reelModel", e.target.value)}
                            name="reelModel"
                            disabled={sharedFields.includes("reelModel") && activePage !== "page1"}
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
                            value={subpageData[activePage].reelWidth || ""}
                            onChange={(e) => handleChange("reelWidth", e.target.value)}
                            name="reelWidth"
                            disabled={sharedFields.includes("reelWidth") && activePage !== "page1"}
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
                            value={subpageData[activePage].backplateDiameter || ""}
                            onChange={(e) => handleChange("backplateDiameter", e.target.value)}
                            name="backplateDiameter"
                            disabled={sharedFields.includes("backplateDiameter") && activePage !== "page1"}
                        >
                            {backplateDiameterOptions.map((diameter) => (
                                <MenuItem key={diameter} value={diameter}>
                                    {diameter}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Type of Line</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].typeOfLine || ""}
                            onChange={(e) => handleChange("typeOfLine", e.target.value)}
                            name="typeOfLine"
                            disabled={sharedFields.includes("typeOfLine") && activePage !== "page1"}
                        >
                            {typeOfLineOptions.map((type) => (
                                <MenuItem key={type} value={type}>
                                    {type}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Horsepower</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].horsepower || ""}
                            onChange={(e) => handleChange("horsepower", e.target.value)}
                            name="horsepower"
                            disabled={sharedFields.includes("horsepower") && activePage !== "page1"}
                        >
                            {horsepowerOptions.map((hp) => (
                                <MenuItem key={hp} value={hp}>
                                    {hp}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Air Clutch</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].airClutch || ""}
                            onChange={(e) => handleChange("airClutch", e.target.value)}
                            name="airClutch"
                            disabled={sharedFields.includes("airClutch") && activePage !== "page1"}
                        >
                            {airClutchOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                    </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Hyd Threading Drive</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].hydThreadingDrive || ""}
                            onChange={(e) => handleChange("hydThreadingDrive", e.target.value)}
                            name="hydThreadingDrive"
                            disabled={sharedFields.includes("hydThreadingDrive") && activePage !== "page1"}
                        >
                            {hydThreadingDriveOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Hold Down Assembly</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].holdDownAssy || ""}
                            onChange={(e) => handleChange("holdDownAssy", e.target.value)}
                            name="holdDownAssy"
                            disabled={sharedFields.includes("holdDownAssy") && activePage !== "page1"}
                        >
                            {holdDownAssyOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                    </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Cylinder</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].cylinder || ""}
                            onChange={(e) => handleChange("cylinder", e.target.value)}
                            name="cylinder"
                            disabled={sharedFields.includes("cylinder") && activePage !== "page1"}
                        >
                            {cylinderOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Brake Quantity</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].brakeQty || ""}
                            onChange={(e) => handleChange("brakeQty", e.target.value)}
                            name={"brakeQty"}
                            disabled={sharedFields.includes("brakeQty") && activePage !== "page1"}
                        >
                            {brakeQtyOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>

                <Grid item xs={6} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Brake Model</Typography>
                    <FormControl fullWidth size="small">
                        <Select
                            value={subpageData[activePage].brakeModel || ""}
                            onChange={(e) => handleChange("brakeModel", e.target.value)}
                            name={"brakeModel"}
                            disabled={sharedFields.includes("brakeModel") && activePage !== "page1"}
                        >
                            {brakeModelOptions.map((option) => (
                                <MenuItem key={option} value={option}>
                                    {option}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Air Pressure Available</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage].airPressure || ""}
                        onChange={(e) => handleChange("airPressure", e.target.value)}
                        fullWidth
                        disabled={sharedFields.includes("airPressure") && activePage !== "page1"}
                    />
                </Grid>

                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Required Deceleration Rate</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage].decel || ""}
                        onChange={(e) => handleChange("decel", e.target.value)}
                        fullWidth
                        disabled={sharedFields.includes("decel") && activePage !== "page1"}
                    />
                </Grid>

                <Grid item xs={12} md={6}>
                    <Typography noWrap style={{ minWidth: 200 }}>Friction</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage].friction || ""}
                        onChange={(e) => handleChange("friction", e.target.value)}
                        fullWidth
                        disabled={sharedFields.includes("friction") && activePage !== "page1"}
                    />
                </Grid>
            </Grid>

            {/* Material Fields for the current subpage */}
            <Typography variant="h6" sx={{ mt: 2 }}>
                {pages.find((p) => p.key === activePage)?.title} Material Properties
            </Typography>
            <Grid container spacing={1} sx={{ mt: 1 }}>
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
                                            value={materialSpecs[field] || ""}
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

            {/* Summary Table */}
            <Divider sx={{ my: 4 }} />
            <Typography variant="h6">Summary of Key Calculated Fields</Typography>
            <Table>
                <TableBody>
                    <TableRow>
                        <TableCell><strong>Calculated Variable</strong></TableCell>
                        <TableCell><strong>Max</strong></TableCell>
                        <TableCell><strong>Full</strong></TableCell>
                        <TableCell><strong>Min</strong></TableCell>
                        <TableCell><strong>Width</strong></TableCell>
                    </TableRow>
                    {["rewindTorque", "coilWidth", "holdDownForceRequired", "brakePressRequired", "torqueRequired"].map((field) => (
                        <TableRow key={field}>
                            <TableCell>{formatLabel(field)}</TableCell>
                            {Object.keys(pageMapping).map((key) => {
                                const suffix = capitalize(pageMapping[key]);
                                const value = subpageData[key]?.[`${field}${suffix}`];
                                const isPass = evaluateCondition(field, key);
                                return (
                                    <TableCell
                                        key={key}
                                        sx={{
                                            backgroundColor: isPass ? `${green}` : `${red}`
                                        }}
                                    >
                                        {value !== undefined ? value : "0"}
                                    </TableCell>
                                );
                            })}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
}
