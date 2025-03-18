import { useState } from "react";
import { Button, TextField, Grid, Typography, Paper, FormControl, InputLabel, Select, MenuItem } from "@mui/material";

export default function MachineSpecs({ rfqId }) {
    const [machines, setMachines] = useState([]);
    const [newMachine, setNewMachine] = useState({
        name: "",
        type: "",
        reel_model: "",
        reel_width: "",
        backplate_diameter: "",
        reel_motorization: "",
        single_or_double: "",
        threading_drive: "",
        air_clutch: "",
        hyd_threading_drive: "",
        hold_down: "",
        hold_down_assy: "",
        length: "",
        spm_180: "",
        spm_240: "",
        feed_rate: ""
    });

    const addMachine = async () => {
        const response = await fetch(`/api/rfq/${rfqId}/add-machine`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newMachine),
        });
        const data = await response.json();
        setMachines([...machines, newMachine]);
        setNewMachine({
            name: "", type: "", reel_model: "", reel_width: "", backplate_diameter: "", reel_motorization: "",
            single_or_double: "", threading_drive: "", air_clutch: "", hyd_threading_drive: "", hold_down: "", hold_down_assy: "",
            length: "", spm_180: "", spm_240: "", feed_rate: ""
        });
    };

    return (
        <Paper className="p-6 max-w-4xl mx-auto shadow-md">
            <Typography variant="h4" gutterBottom>Machine Specifications</Typography>
            <Typography variant="body1" paragraph>Provide detailed specifications for each machine.</Typography>

            <Grid container spacing={3}>
                <Grid item xs={12}><Typography variant="h6">General Machine Information</Typography></Grid>
                <Grid item xs={12} sm={6}><TextField label="Machine Name" value={newMachine.name} onChange={(e) => setNewMachine({ ...newMachine, name: e.target.value })} fullWidth /></Grid>
                <Grid item xs={12} sm={6}><TextField label="Machine Type" value={newMachine.type} onChange={(e) => setNewMachine({ ...newMachine, type: e.target.value })} fullWidth /></Grid>

                <Grid item xs={12}><Typography variant="h6">Reel Specifications</Typography></Grid>
                {[
                    "reel_model", "reel_width", "backplate_diameter", "reel_motorization", "single_or_double", "threading_drive",
                    "air_clutch", "hyd_threading_drive", "hold_down", "hold_down_assy"
                ].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField label={field.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase())} value={newMachine[field]} onChange={(e) => setNewMachine({ ...newMachine, [field]: e.target.value })} fullWidth />
                    </Grid>
                ))}

                <Grid item xs={12}><Typography variant="h6">Sigma 5 Feed Specifications</Typography></Grid>
                {[
                    "length", "spm_180", "spm_240", "feed_rate"
                ].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                        <TextField label={field.replace("_", " ").replace(/\b\w/g, c => c.toUpperCase())} value={newMachine[field]} onChange={(e) => setNewMachine({ ...newMachine, [field]: e.target.value })} fullWidth />
                    </Grid>
                ))}

                <Grid item xs={12} className="text-center">
                    <Button onClick={addMachine} variant="contained" color="primary">Add Machine</Button>
                </Grid>

                <Grid item xs={12}><Typography variant="h6">Added Machines</Typography></Grid>
                {machines.length === 0 ? (
                    <Grid item xs={12}><Typography variant="body2">No machines added yet.</Typography></Grid>
                ) : (
                    machines.map((machine, index) => (
                        <Grid item xs={12} key={index}>
                            <Paper className="p-3 shadow-sm">
                                <Typography variant="body1"><strong>{machine.name}</strong> ({machine.type})</Typography>
                            </Paper>
                        </Grid>
                    ))
                )}
            </Grid>
        </Paper>
    );
}