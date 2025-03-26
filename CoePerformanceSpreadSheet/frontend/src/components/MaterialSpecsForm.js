import { useState, useContext, useEffect } from "react";
import { Button, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableRow, Grid, Divider, TextField } from "@mui/material";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
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
            const response = await fetch("/api                                                 /rfq/latest"); // Adjust API route if needed
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
                yieldStrengthMax: rfqData.max_yield_strength || prev.yieldStrengthMax,
                coilIDMax: rfqData.coil_inner_diameter || prev.coilIDMax,
                coilODMax: rfqData.coil_outer_diameter || prev.coilODMax,

                coilWidthFull: rfqData.max_material_at_width || prev.coilWidthFull,
                coilWeightFull: rfqData.max_coil_weight || prev.coilWeightFull,
                materialThicknessFull: rfqData.max_material_thickness || prev.materialThicknessFull,
                materialTypeFull: rfqData.max_material_material_type || prev.materialTypeFull,
                yieldStrengthFull: rfqData.max_material_strength || prev.yieldStrengthFull,
                coilIDFull: rfqData.coil_inner_diameter || prev.coilIDFull,
                coilODFull: rfqData.coil_outer_diameter || prev.coilODFull,

                coilWidthMin: rfqData.min_yield_at_width || prev.coilWidthMin,
                coilWeightMin: rfqData.max_coil_weight || prev.coilWeightMin,
                materialThicknessMin: rfqData.min_material_thickness || prev.materialThicknessMin,
                materialTypeMin: rfqData.min_material_material_type || prev.materialTypeMin,
                yieldStrengthMin: rfqData.min_material_strength || prev.yieldStrengthMin,
                coilIDMin: rfqData.coil_inner_diameter || prev.coilIDMin,
                coilODMin: rfqData.coil_outer_diameter || prev.coilODMin,

                coilWidthWidth: rfqData.max_material_run_at_width || prev.coilWidthWidth,
                coilWeightWidth: rfqData.max_coil_weight || prev.coilWeightWidth,
                materialThicknessWidth: rfqData.max_material_run_thickness || prev.materialThicknessWidth,
                materialTypeWidth: rfqData.max_material_run_material_type || prev.materialTypeWidth,
                yieldStengthWidth: rfqData.max_material_run_strength || prev.yieldStrengthWidth,
                coilIDWidth: rfqData.coil_inner_diameter || prev.coilIDWidth,
                coilODWidth: rfqData.coil_outer_diameter || prev.coilODWidth,

            }));
        } catch (error) {
            console.error("Error fetching RFQ data:", error);
        }
    };

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
                    {["coilWidthMax", "coilWeightMax", "materialThicknessMax", "materialTypeMax",
                      "yieldStrengthMax", "materialTensileMax", "requiredMaxFPMMax", "minBendRadiusMax",
                      "minLoopLengthMax", "coilODMax", "coilIDMax", "coilODCalculatedMax"].map((field) => (
                        <Grid item xs={12} sm={4} key={field}>
                            <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                        </Grid>
                      ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Max @ Full</Typography></Grid>
                    {["coilWidthFull", "coilWeightFull", "materialThicknessFull", "materialTypeFull",
                        "yieldStrengthFull", "materialTensileFull", "requiredMaxFPMFull", "minBendRadiusFull",
                        "minLoopLengthFull", "coilODFull", "coilIDFull", "coilODCalculatedFull"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Min Thickness</Typography></Grid>
                    {["coilWidthMin", "coilWeightMin", "materialThicknessMin", "materialTypeMin",
                        "yieldStrengthMin", "materialTensileMin", "requiredMaxFPMMin", "minBendRadiusMin",
                        "minLoopLengthMin", "coilODMin", "coilIDMin", "coilODCalculatedMin"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>

                <Table container>
                    <Grid item xs={12}><Divider /><Typography variant="h5">Max @ Width</Typography></Grid>
                    {["coilWidthWidth", "coilWeightWidth", "materialThicknessWidth", "materialTypeWidth",
                        "yieldStrengthWidth", "materialTensileWidth", "requiredMaxFPMWidth", "minBendRadiusWidth",
                        "minLoopLengthWidth", "coilODWidth", "coilIDWidth", "coilODCalculatedWidth"].map((field) => (
                            <Grid item xs={12} sm={4} key={field}>
                                <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                            </Grid>
                        ))}
                </Table>
            </Grid>

            <Grid item xs={12}><Divider /><Typography variant="h5">Feed System</Typography></Grid>
            {["feedDirection", "controlsLevel", "typeOfLine", "feedControls", "passline"].map((field) => (
                <Grid item xs={12} sm={4} key={field}>
                    <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                </Grid>
            ))}

            <Grid item xs={12}><Divider /><Typography variant="h5">Roll Selection</Typography></Grid>
            {["selectRoll"].map((field) => (
                <Grid item xs={12} sm={4} key={field}>
                    <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                </Grid>
            ))}

            <Grid item xs={12}><Divider /><Typography variant="h5">Reel Information</Typography></Grid>
            {["reelBackplate", "reelStyle"].map((field) => (
                <Grid item xs={12} sm={4} key={field}>
                    <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                </Grid>
            ))}

            <Grid item xs={12}><Divider /><Typography variant="h5">Non-Marking</Typography></Grid>
            {["lightGuageNonMarking", "nonMarking"].map((field) => (
                <Grid item xs={12} sm={4} key={field}>
                    <TextField size="small" label={formatLabel(field)} type="number" value={materialSpecs[field]} onChange={(e) => handleChange(field, e.target.value)} fullWidth />
                </Grid>
            ))}

            {/* Pull Data Button */}
            <Button variant="contained" color="primary" className="mt-4" fullWidth onClick={fetchRFQData}>
                Pull Data from RFQ
            </Button>
        </Paper>
    );
}
