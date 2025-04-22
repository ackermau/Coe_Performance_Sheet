import React, { useEffect, useState, useContext } from "react";
import {
    Paper, Typography, Divider, Grid, Table, TableBody,
    TableCell, TableContainer, TableRow, TextField, CircularProgress
} from "@mui/material";
import { API_URL } from "../config";
import { MaterialSpecsContext } from "../context/MaterialSpecsContext";
import { ReelDriveContext } from "../context/ReelDriveContext";

export default function ReelDrive() {
    const { materialSpecs } = useContext(MaterialSpecsContext);
    const [form, setForm] = useState({});
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const { reelDriveData, setReelDriveData } = useContext(ReelDriveContext);
    const tqEmpty = data?.torque?.empty || 0; // Default to 0 if undefined

    useEffect(() => {
        const updatedForm = {
            model: "CPR-200",
            material_type: materialSpecs.materialTypeMax || "Cold Rolled Steel",
            coil_weight: parseFloat(materialSpecs.coilWeightMax) || 20000,
            coil_id: parseFloat(materialSpecs.coilIDMax) || 20,
            coil_od: parseFloat(materialSpecs.coilODMax) || 72,
            reel_width: parseFloat(materialSpecs.coilWidthMax) || 42,
            backplate_diameter: 27, // Static or can map from specs
            motor_hp: 5,
            type_of_line: materialSpecs.lineType || "Motorized",
            required_max_fpm: parseFloat(materialSpecs.requiredMaxFPMMax) || 35,
        };
        setForm(updatedForm);
    }, [materialSpecs]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/reel_drive/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });
            const result = await res.json();
            setData(result);
            if (result?.torque?.empty !== undefined) {
                setReelDriveData({ torque_empty: result.torque.empty });
                console.log("Torque empty:", result.torque.empty);
            }
        } catch (err) {
            console.error("Calculation error:", err);
            setData(null);
        }
        setLoading(false);
    };

    useEffect(() => {
        if (Object.keys(form).length > 0) {
            fetchData();
        }
    }, [form]);

    const getValue = (section, field) => {
        if (!data) return "";
        const val = data[section]?.[field];
        if (val === undefined) return "";
        return typeof val === "number" ? val.toFixed(2) : val;
    };

    const renderSection = (title, fieldMap) => (
        <>
            <Typography variant="h6" sx={{ mt: 3 }}>{title}</Typography>
            <TableContainer component={Paper} sx={{ mb: 2 }}>
                <Table size="small">
                    <TableBody>
                        {fieldMap.map((row, idx) => (
                            <TableRow key={idx}>
                                {row.map(([section, field]) => (
                                    <TableCell key={field}>
                                        <strong>{field.replace(/_/g, " ").toUpperCase()}</strong><br />
                                        {getValue(section, field)}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );

    return (
        <Paper sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>COE PRESS EQUIPMENT CORPORATION</Typography>
            <Typography variant="subtitle1">Input Parameters (Auto-Populated)</Typography>

            <Grid container spacing={2} sx={{ mb: 2 }}>
                {Object.entries(form).map(([key, value]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                        <TextField
                            fullWidth
                            label={key.replace(/_/g, " ").toUpperCase()}
                            value={value}
                            InputProps={{ readOnly: true }}
                        />
                    </Grid>
                ))}
            </Grid>

            <Divider sx={{ my: 2 }} />

            {loading ? (
                <CircularProgress />
            ) : !data ? (
                <Typography variant="body1">Waiting for calculation...</Typography>
            ) : (
                <>
                    {renderSection("Reel", [
                        [["reel", "size"], ["reel", "max_width"], ["reel", "brg_dist"], ["reel", "f_brg_dia"], ["reel", "r_brg_dia"]]
                    ])}
                    {renderSection("Mandrel", [
                        [["mandrel", "diameter"], ["mandrel", "length"], ["mandrel", "max_rpm"], ["mandrel", "rpm_full"]],
                        [["mandrel", "weight"], ["mandrel", "inertia"], ["mandrel", "refl_inert"]]
                    ])}
                    {renderSection("Backplate", [
                        [["backplate", "diameter"], ["backplate", "thickness"], ["backplate", "weight"], ["backplate", "inertia"], ["backplate", "refl_inert"]]
                    ])}
                    {renderSection("Coil", [
                        [["coil", "density"], ["coil", "od"], ["coil", "id"], ["coil", "width"]],
                        [["coil", "weight"], ["coil", "inertia"], ["coil", "refl_inert"]]
                    ])}
                    {renderSection("Reducer", [
                        [["reducer", "ratio"], ["reducer", "driving"], ["reducer", "backdriving"], ["reducer", "inertia"], ["reducer", "refl_inert"]]
                    ])}
                    {renderSection("Chain", [
                        [["chain", "ratio"], ["chain", "sprkt_od"], ["chain", "sprkt_thk"]],
                        [["chain", "weight"], ["chain", "inertia"], ["chain", "refl_inert"]]
                    ])}
                    {renderSection("Total Inertia", [
                        [["total", "ratio"], ["total", "total_refl_inert_empty"], ["total", "total_refl_inert_full"]]
                    ])}
                    {renderSection("Motor", [
                        [["motor", "hp"], ["motor", "inertia"], ["motor", "base_rpm"], ["motor", "rpm_full"]]
                    ])}
                    {renderSection("Friction", [
                        [["friction", "r_brg_mand"], ["friction", "f_brg_mand"]],
                        [["friction", "r_brg_coil"], ["friction", "f_brg_coil"]],
                        [["friction", "total_empty"], ["friction", "total_full"]],
                        [["friction", "refl_empty"], ["friction", "refl_full"]]
                    ])}
                    {renderSection("Speed & Acceleration", [
                        [["speed", "speed"], ["speed", "accel_rate"], ["speed", "accel_time"]]
                    ])}
                    {renderSection("Torque & Power", [
                        [["torque", "empty"], ["torque", "full"]],
                        [["hp_req", "empty"], ["hp_req", "full"]],
                        [["hp_req", "status_empty"], ["hp_req", "status_full"]]
                    ])}
                    {renderSection("Regeneration", [
                        [["regen", "empty"], ["regen", "full"]],
                        [["", "use_pulloff"]]
                    ])}
                </>
            )}
        </Paper>
    );
}
