// FULL VERSION: TddbhdPage restored to original layout with full field logic and integrated ReelDrive + backend calculation

import { useState, useEffect, useContext } from "react";
import {
    Paper, Typography, Grid, Divider, TextField, FormControl, Select, MenuItem, Button, Table, TableBody, TableRow, TableCell, CircularProgress
} from "@mui/material";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { RFQFormContext } from "../context/RFQFormContext";
import { TddbhdContext } from "../context/TddbhdContext";
import { ReelDriveContext } from "../context/ReelDriveContext";
import { API_URL } from '../config';

const formatLabel = (label) => label
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase())
    .replace(/([a-z])([A-Z])/g, "$1 $2");

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const pageMapping = { page1: "max", page2: "full", page3: "min", page4: "width" };
const brakeQtyOptions = ["1", "2", "3"];
const brakeModelOptions = ["Single Stage", "Double Stage", "Triple Stage", "Failsafe - Single Stage", "Failsafe - Double Stage"];
const airClutchOptions = ["Yes", "No"];
const hydThreadingDriveOptions = ["22 cu in (D-12689)", "38 cu in (D-13374)", "60 cu in (D-13374)", "60 cu in (D-13382)"];
const holdDownAssyOptions = ["SD", "SD_MOTORIZED", "MD", "HD_SINGLE", "HD_DUAL", "XD", "XXD"];
const cylinderOptions = ["Hydraulic"];
const materialOptions = ["Aluminum", "Galvanized", "HS Steel", "Hot Rolled Steel", "Dual Phase", "Cold Rolled Steel", "Stainless Steel", "Titanium", "Brass", "Beryl Copper"];

const groupFields = {
    max: ["coilWidthMax", "materialThicknessMax", "yieldStrengthMax", "coilIDMax", "coilODMax", "frictionMax", "webTensionPsiMax", "torqueRequiredMax", "brakePressRequiredMax", "brakePressHoldingForceMax"],
    full: ["coilWidthFull", "materialThicknessFull", "yieldStrengthFull", "coilIDFull", "coilODFull", "frictionFull", "webTensionPsiFull", "torqueRequiredFull", "brakePressRequiredFull", "brakePressHoldingForceFull"],
    min: ["coilWidthMin", "materialThicknessMin", "yieldStrengthMin", "coilIDMin", "coilODMin", "frictionMin", "webTensionPsiMin", "torqueRequiredMin", "brakePressRequiredMin", "brakePressHoldingForceMin"],
    width: ["coilWidthWidth", "materialThicknessWidth", "yieldStrengthWidth", "coilIDWidth", "coilODWidth", "frictionWidth", "webTensionPsiWidth", "torqueRequiredWidth", "brakePressRequiredWidth", "brakePressHoldingForceWidth"]
};
const reelModels = [
    "CPR-040", "CPR-060", "CPR-080", "CPR-100",
    "CPR-200", "CPR-300", "CPR-400", "CPR-500", "CPR-600"
];

export default function TddbhdPage() {
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const { subpageData, setSubpageData, activePage, setActivePage } = useContext(TddbhdContext);
    const { reelDriveData, setReelDriveData } = useContext(ReelDriveContext);

    const suffix = pageMapping[activePage];
    const capSuffix = capitalize(suffix);
    const [loading, setLoading] = useState(false);

    const getDefaultDataForGroup = (group) => {
        const suffix = capitalize(group);
        return {
            reelModel: "CPR-200",
            reelWidth: 42,
            backplateDiameter: 27,
            typeOfLine: "PULLOFF",
            driveTorque: "",
            reelDriveTQEmpty: "",
            brakeQty: "1",
            brakeModel: brakeModelOptions[0],
            airClutch: airClutchOptions[0],
            hydThreadingDrive: hydThreadingDriveOptions[0],
            holdDownAssy: holdDownAssyOptions[0],
            cylinder: cylinderOptions[0],
            airPressure: "",
            decel: "",
            ...Object.fromEntries(
                groupFields[group].map(f => [f, materialSpecs?.[f] || ""])
            )
        };
    };

    const calculateReelDrive = async () => {
        const form = {
            model: "CPR-200",
            material_type: materialSpecs.materialTypeMax || "Cold Rolled Steel",
            coil_weight: parseFloat(materialSpecs.coilWeightMax) || 20000,
            coil_id: parseFloat(materialSpecs.coilIDMax) || 20,
            coil_od: parseFloat(materialSpecs.coilODMax) || 72,
            reel_width: parseFloat(materialSpecs.coilWidthMax) || 42,
            backplate_diameter: 27,
            motor_hp: 5,
            type_of_line: materialSpecs.lineType || "Motorized",
            required_max_fpm: parseFloat(materialSpecs.requiredMaxFPMMax) || 35,
        };
        try {
            const res = await fetch(`${API_URL}/api/reel_drive/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });
            const result = await res.json();
            setReelDriveData(prev => ({ ...prev, torque_empty: result?.torque?.empty || 0 }));
        } catch (err) {
            console.error("ReelDrive calculation failed:", err);
        }
    };

    useEffect(() => {
        setSubpageData(prev => {
            const updated = { ...prev };
            Object.keys(pageMapping).forEach(key => {
                if (!updated[key]) updated[key] = getDefaultDataForGroup(pageMapping[key]);
            });
            return updated;
        });
    }, []);

    useEffect(() => {
        const runCalc = async () => {
            setLoading(true);
            await calculateReelDrive();
            setLoading(false);
        };
        runCalc();
    }, []);

    useEffect(() => {
        if (reelDriveData?.torque_empty !== undefined) {
            setSubpageData(prev => ({
                ...prev,
                [activePage]: {
                    ...prev[activePage],
                    reelDriveTQEmpty: reelDriveData.torque_empty.toFixed(2)
                }
            }));
        }
    }, [reelDriveData?.torque_empty, activePage]);

    const handleChange = (field, value) => {
        setSubpageData(prev => ({
            ...prev,
            [activePage]: {
                ...prev[activePage],
                [field]: value
            }
        }));
    };

    const buildTddbhdPayload = () => {
        const data = subpageData[activePage];
        return {
            type_of_line: data.typeOfLine,
            drive_torque: Number(data.driveTorque) || 0,
            reel_drive_tqempty: Number(data.reelDriveTQEmpty || 0),
            yield_strength: Number(data[`yieldStrength${capSuffix}`]) || 0,
            thickness: Number(data[`materialThickness${capSuffix}`]) || 0,
            width: Number(data[`coilWidth${capSuffix}`]) || 0,
            coil_id: Number(data[`coilID${capSuffix}`]) || 0,
            coil_od: Number(data[`coilOD${capSuffix}`]) || 0,
            friction: Number(data[`friction${capSuffix}`]) || 0,
            air_pressure: Number(data[`airPressure`]) || 0,
            max_psi: Number(data[`maxPsi${capSuffix}`]) || 0,
            holddown_pressure: Number(data[`holddownPressure${capSuffix}`]) || 0,
            brake_qty: Number(data[`brakeQty`]) || 1,
            brake_model: data[`brakeModel`] || "",
            cylinder: data[`cylinder`] || "",
            hold_down_assy: data[`holdDownAssy`] || "",
            hyd_threading_drive: data[`hydThreadingDrive`] || "",
            air_clutch: data[`airClutch`] || "",
            material_type: data[`materialType${capSuffix}`] || "Cold Rolled Steel",
            reel_model: data.reelModel || "",
            coil_weight: data.maxCoilWeight || 0,
        };
    };

    const triggerBackendCalculation = async () => {
        const payload = buildTddbhdPayload();
        try {
            const res = await fetch(`${API_URL}/api/tddbhd/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await res.json();
            console.log("Tddbhd result:", result);
        } catch (err) {
            console.error("Tddbhd backend calculation failed:", err);
        }
    };

    useEffect(() => {
        if (subpageData[activePage]?.reelDriveTQEmpty) {
            triggerBackendCalculation();
        }
    }, [subpageData, activePage]);

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
                TB/DB/HD Machine Simulation - {capitalize(suffix)}
            </Typography>
            <Divider sx={{ my: 2 }} />

            {loading ? <CircularProgress /> : (
                <>
                    <Typography variant="h6">Reel Setup</Typography>
                    <Grid container spacing={2}>
                        {renderSelect("reelModel", ["CPR-040", "CPR-060", "CPR-080", "CPR-100", "CPR-200"])}
                        {renderSelect("reelWidth", [42, 48, 54, 60, 66, 72])}
                        {renderSelect("backplateDiameter", [27, 72])}
                    </Grid>

                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6">Material + Mechanical Inputs</Typography>
                    <Grid container spacing={2}>
                        {groupFields[suffix].map(renderTextField)}
                        {renderTextField("driveTorque")}
                        {renderTextField("reelDriveTQEmpty")}
                    </Grid>

                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6">Brake, Cylinder, Hold Down</Typography>
                    <Grid container spacing={2}>
                        {renderSelect("brakeQty", brakeQtyOptions)}
                        {renderSelect("brakeModel", brakeModelOptions)}
                        {renderSelect("airClutch", airClutchOptions)}
                        {renderSelect("hydThreadingDrive", hydThreadingDriveOptions)}
                        {renderSelect("holdDownAssy", holdDownAssyOptions)}
                        {renderSelect("cylinder", cylinderOptions)}
                        {renderTextField("airPressure")}
                        {renderTextField("decel")}
                    </Grid>
                </>
            )}

            <Divider sx={{ my: 3 }} />
            <Grid container spacing={2} justifyContent="space-between">
                <Grid item>
                    <Button
                        variant="contained"
                        disabled={activePage === "page1"}
                        onClick={() => {
                            const keys = Object.keys(pageMapping);
                            const current = keys.indexOf(activePage);
                            if (current > 0) setActivePage(keys[current - 1]);
                        }}
                    >Back</Button>
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        disabled={activePage === "page4"}
                        onClick={() => {
                            const keys = Object.keys(pageMapping);
                            const current = keys.indexOf(activePage);
                            if (current < keys.length - 1) setActivePage(keys[current + 1]);
                        }}
                    >Next</Button>
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
                                return (
                                    <TableCell key={key}>
                                        {value !== undefined ? value : "–"}
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
