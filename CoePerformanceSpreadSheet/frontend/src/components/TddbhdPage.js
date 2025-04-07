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

const formatLabel = (label) => {
    return label
        .replace(/_/g, " ")
        .replace(/\b\w/g, (char) => char.toUpperCase())
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        .replace(/\s*(Max|Full|Min|Width)$/i, "");
};

const reelModels = [
    "CPR-040",
    "CPR-060",
    "CPR-080",
    "CPR-100",
    "CPR-200",
    "CPR-300",
    "CPR-400",
    "CPR-500",
    "CPR-600"
];

const reelWidths = [42, 48, 54, 60, 66, 72];

const backplateDiameters = [27, 72];

const materialOptions = [
    "Aluminum",
    "Galvanized",
    "HS Steel",
    "Hot Rolled Steel",
    "Dual Phase",
    "Cold Rolled Steel",
    "Stainless Steel",
    "Titanium",
    "Brass",
    "Beryl Copper"
];

// Define the material field groups for each subpage.
const groupFields = {
    max: ["materialTypeMax", "coilWidthMax", "materialThicknessMax", "yieldStrengthMax"],
    full: ["materialTypeFull", "coilWidthFull", "materialThicknessFull", "yieldStrengthFull"],
    min: ["materialTypeMin", "coilWidthMin", "materialThicknessMin", "yieldStrengthMin"],
    width: ["materialTypeWidth", "coilWidthWidth", "materialThicknessWidth", "yieldStrengthWidth"]
};

// Helper to build the default state for a given group.

const getDefaultDataForGroup = (group, materialSpecs) => {
  const defaults = {
    reel_model: reelModels[0],
    reel_width: reelWidths[0],
    backplate_diameter: backplateDiameters[0],
    // Additional fields needed by the tddbhd payload:
    type_of_line: "PULLOFF",        // default example
    drive_torque: "",
    reel_drive_tqempty: "",
    // We assume these material-related fields are set per view:
    ...groupFields[group].reduce((acc, field) => {
      acc[field] = materialSpecs && materialSpecs[field] ? materialSpecs[field] : "";
      return acc;
    }, {}),
    // Other fields required by the tddbhd payload – you may need to add input fields for these
    thickness: "",        // e.g. material thickness (inches)
    width: "",            // overall width value
    coil_id: "",          // coil ID
    coil_od: "",          // coil OD if provided
    coil_weight: "",      // coil weight in lbs
    density: "",          // material density
    max_weight: 60000,    // default maximum weight
    tension_torque: "",
    decel: "",
    y: "",
    M: "",
    My: "",
    friction: "",
    air_pressure: "",
    max_psi: "",
    holddown_pressure: "",
    holddown_force_factor: "",
    holddown_min_width: "",
    brake_qty: "",
    no_brakepads: "",
    brake_dist: "",
    press_force_required: "",
    press_force_holding: "",
    holddown_matrix_label: "psi air" // example default
  };
  return defaults;
};

export default function TddbhdPage() {
    const { rfqForm } = useContext(RFQFormContext);
    const { materialSpecs } = useContext(MaterialSpecsContext);

    // Map subpage keys to group names.
    const pageMapping = {
        page1: "max",
        page2: "full",
        page3: "min",
        page4: "width"
    };

    // Initialize state for each subpage with its corresponding group.
    const [subpageData, setSubpageData] = useState({
        page1: getDefaultDataForGroup("max", materialSpecs),
        page2: getDefaultDataForGroup("full", materialSpecs),
        page3: getDefaultDataForGroup("min", materialSpecs),
        page4: getDefaultDataForGroup("width", materialSpecs)
    });

    // Track the active subpage.
    const [activePage, setActivePage] = useState("page1");

    // Update subpage data if materialSpecs changes.
    useEffect(() => {
        setSubpageData({
            page1: getDefaultDataForGroup("max", materialSpecs),
            page2: getDefaultDataForGroup("full", materialSpecs),
            page3: getDefaultDataForGroup("min", materialSpecs),
            page4: getDefaultDataForGroup("width", materialSpecs)
        });
    }, [materialSpecs]);

    // Update field value for the active subpage.
    const handleChange = (field, value) => {
        setSubpageData((prev) => ({
            ...prev,
            [activePage]: { ...prev[activePage], [field]: value }
        }));
        // Optionally trigger a backend calculation with the updated active page data.
        triggerBackendCalculation({ ...subpageData[activePage], [field]: value });
    };

    const triggerBackendCalculation = async (payload) => {
        try {
            const response = await fetch("/api/tddbhd/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            setSubpageData((prev) => ({
                ...prev,
                [activePage]: { ...prev[activePage], ...data }
            }));
        } catch (err) {
            console.error("Backend calculation failed:", err);
        }
    };

    // Define the subpages.
    const pages = [
        { key: "page1", title: "Max" },
        { key: "page2", title: "Full" },
        { key: "page3", title: "Min" },
        { key: "page4", title: "Width" }
    ];

    const goToPreviousPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex > 0) {
            setActivePage(pages[currentIndex - 1].key);
        }
    };

    const goToNextPage = () => {
        const currentIndex = pages.findIndex((page) => page.key === activePage);
        if (currentIndex < pages.length - 1) {
            setActivePage(pages[currentIndex + 1].key);
        }
    };

    // Determine which material fields to render based on the active subpage.
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
                            value={subpageData[activePage].reel_model}
                            onChange={(e) => handleChange("reel_model", e.target.value)}
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
                            value={subpageData[activePage].reel_width}
                            onChange={(e) => handleChange("reel_width", e.target.value)}
                            name="reel_width"
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
                            value={subpageData[activePage].backplate_diameter}
                            onChange={(e) => handleChange("backplate_diameter", e.target.value)}
                            name="backplate_diameter"
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

            {/* Material Fields for the current subpage */}
            <Typography variant="h6" sx={{ mt: 2 }}>
                {pages.find((p) => p.key === activePage)?.title} Material Properties
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
                {currentGroupFields.map((field) => (
                    <Grid item xs={12} sm={4} key={field}>
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
                            <TextField
                                size="small"
                                label={formatLabel(field)}
                                value={subpageData[activePage][field] || ""}
                                onChange={(e) => handleChange(field, e.target.value)}
                                type="number"
                                fullWidth
                            />
                        )}
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Air Pressure Available</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage].air_pressure_available || ""}
                        onChange={(e) => handleChange("air_pressure_available", e.target.value)}
                        fullWidth
                    />
                </Grid>

                <Grid item xs={12} md={4}>
                    <Typography noWrap style={{ minWidth: 200 }}>Required Deceleration Rate</Typography>
                    <TextField size="small"
                        type="number"
                        value={subpageData[activePage].req_decel_rate || ""}
                        onChange={(e) => handleChange("req_decel_rate", e.target.value)}
                        fullWidth
                    />
                </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            {/* Calculated fields for the current subpage */}
            {subpageData[activePage].web_tension_psi !== "" && (
                <>
                    <Typography variant="h6" sx={{ mt: 4 }}>
                        Calculated Values
                    </Typography>
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell>Web Tension PSI</TableCell>
                                <TableCell>{subpageData[activePage].web_tension_psi}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Web Tension Lbs</TableCell>
                                <TableCell>{subpageData[activePage].web_tension_lbs}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Coil Weight</TableCell>
                                <TableCell>{subpageData[activePage].coil_weight}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Coil OD</TableCell>
                                <TableCell>{subpageData[activePage].coil_od}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Display Reel Motor</TableCell>
                                <TableCell>{subpageData[activePage].disp_reel_mtr}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Torque At Mandrel</TableCell>
                                <TableCell>{subpageData[activePage].torque_at_mandrel}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Rewind Torque</TableCell>
                                <TableCell>{subpageData[activePage].rewind_torque}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Hold Down Force Required</TableCell>
                                <TableCell>{subpageData[activePage].hold_down_force_required}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Hold Down Force Available</TableCell>
                                <TableCell>{subpageData[activePage].hold_down_force_available}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Min Material Width</TableCell>
                                <TableCell>{subpageData[activePage].min_material_width}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Torque Required</TableCell>
                                <TableCell>{subpageData[activePage].torque_required}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Failsafe Double Stage</TableCell>
                                <TableCell>{subpageData[activePage].failsafe_double_stage}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Failsafe Holding Force</TableCell>
                                <TableCell>{subpageData[activePage].failsafe_holding_force}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </>
            )}

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
